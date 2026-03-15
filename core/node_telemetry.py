"""
Node Telemetry Engine — real-time member QR node analytics.

Each Helios member QR code is a live node. This engine provides:
- Event emission (emit_event) — log any QR/join/wallet/issuance event
- Node stats (get_node_stats) — scans, joins, chain depth, rewards
- Propagation tree (get_propagation_tree) — full network ancestry
- Conversion funnel (get_conversion_funnel) — QR scan → join → activate
- Chain visualization data (get_chain_data) — for d3/network-viz rendering
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Optional

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from models.node_event import NodeEvent
from models.member import Member


class NodeTelemetry:
    """Telemetry spine for Helios member QR nodes."""

    def __init__(self, db_session: Session):
        self.db = db_session

    # ═══ Event Emission ═══════════════════════════════════════════════

    def emit(
        self,
        event_type: str,
        issuer_slug: str,
        *,
        issuer_wallet: str = None,
        referral_code: str = None,
        parent_member_id: str = None,
        child_member_id: str = None,
        session_id: str = None,
        device_id: str = None,
        ip_hash: str = None,
        user_agent: str = None,
        amount_paid: float = None,
        hls_amount: float = None,
        offer_code: str = None,
        tx_hash: str = None,
        nft_token_ids: list = None,
        chain_depth: int = None,
        chain_path: list = None,
        network_size_after: int = None,
        status: str = "completed",
        error_code: str = None,
        error_detail: str = None,
        metadata: dict = None,
    ) -> NodeEvent:
        """Emit a single node event into the telemetry spine."""
        event = NodeEvent(
            event_type=event_type,
            issuer_slug=issuer_slug,
            issuer_wallet=issuer_wallet,
            referral_code=referral_code,
            parent_member_id=parent_member_id,
            child_member_id=child_member_id,
            session_id=session_id,
            device_id=device_id,
            ip_hash=ip_hash,
            user_agent=user_agent,
            amount_paid=amount_paid,
            hls_amount=hls_amount,
            offer_code=offer_code,
            tx_hash=tx_hash,
            nft_token_ids=nft_token_ids,
            chain_depth=chain_depth,
            chain_path=chain_path,
            network_size_after=network_size_after,
            status=status,
            error_code=error_code,
            error_detail=error_detail,
            extra=metadata,
        )
        self.db.add(event)
        self.db.commit()
        return event

    # ═══ Node Stats ═══════════════════════════════════════════════════

    def get_node_stats(self, issuer_slug: str) -> dict:
        """
        Get live stats for a member's QR node.
        Returns: total_scans, total_joined, chain_depth,
                 connection_rewards, conversion_rate, last_activation.
        """
        slug = issuer_slug.replace(".helios", "")

        # Total QR scans (qr_scan + qr_view + card_view + drop_view)
        total_scans = self.db.query(func.count(NodeEvent.id)).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.event_type.in_(["qr_scan", "qr_view", "card_view", "drop_view"])
        ).scalar() or 0

        # Total joined through this node
        total_joined = self.db.query(func.count(NodeEvent.id)).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.event_type == "member_created"
        ).scalar() or 0

        # Max chain depth
        max_depth = self.db.query(func.max(NodeEvent.chain_depth)).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.event_type.in_(["member_created", "child_node_created"])
        ).scalar() or 0

        # Connection rewards — sum of reward_accrued events
        total_rewards = self.db.query(func.coalesce(func.sum(NodeEvent.hls_amount), 0)).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.event_type.in_(["reward_accrued", "reward_distributed"])
        ).scalar() or 0.0

        # Total revenue through this node
        total_revenue = self.db.query(func.coalesce(func.sum(NodeEvent.amount_paid), 0)).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.event_type == "payment_completed"
        ).scalar() or 0.0

        # Last activation timestamp
        last_activation = self.db.query(NodeEvent.timestamp).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.event_type == "member_created"
        ).order_by(NodeEvent.timestamp.desc()).first()

        # Conversion rate
        conversion_rate = (total_joined / total_scans * 100) if total_scans > 0 else 0.0

        # Node status (Green/Yellow/Red based on activity)
        status = self._compute_node_status(slug, total_scans, total_joined)

        return {
            "node": f"{slug}.helios",
            "status": status,
            "total_scans": total_scans,
            "total_joined": total_joined,
            "chain_depth": max_depth,
            "connection_rewards": round(total_rewards, 2),
            "total_revenue": round(total_revenue, 2),
            "conversion_rate": round(conversion_rate, 1),
            "last_activation": last_activation[0].isoformat() if last_activation else None,
        }

    def _compute_node_status(self, slug: str, scans: int, joined: int) -> str:
        """
        3-tier node status:
          Green  = active (event in last 7 days)
          Yellow = idle (event in last 30 days but not 7)
          Red    = dormant (no events in 30 days)
        """
        cutoff_7 = datetime.now(timezone.utc) - timedelta(days=7)
        cutoff_30 = datetime.now(timezone.utc) - timedelta(days=30)

        recent = self.db.query(NodeEvent.id).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.timestamp >= cutoff_7
        ).first()
        if recent:
            return "green"

        recent_30 = self.db.query(NodeEvent.id).filter(
            NodeEvent.issuer_slug == slug,
            NodeEvent.timestamp >= cutoff_30
        ).first()
        if recent_30:
            return "yellow"

        return "red"

    # ═══ Propagation Tree ═════════════════════════════════════════════

    def get_propagation_tree(self, root_slug: str, max_depth: int = 15) -> dict:
        """
        Build the full propagation tree from a root member node.
        Each node shows: member, children, depth, stats.
        """
        root_slug = root_slug.replace(".helios", "")

        # Get all members and build tree from referrer_id chains
        members = self.db.query(Member).filter(
            Member.status == "active"
        ).all()

        # Build adjacency map: referrer_id → list of children
        children_map = defaultdict(list)
        member_map = {}
        for m in members:
            slug = m.helios_id.replace(".helios", "")
            member_map[slug] = m
            if m.referrer_id:
                parent_slug = m.referrer_id.replace(".helios", "")
                children_map[parent_slug].append(slug)

        def build_subtree(slug: str, depth: int) -> dict:
            node = member_map.get(slug)
            result = {
                "member": f"{slug}.helios",
                "depth": depth,
                "node_state": node.node_state if node else "unknown",
                "bond_count": node.bond_count if node else 0,
                "children": [],
            }
            if depth < max_depth:
                for child_slug in children_map.get(slug, []):
                    result["children"].append(build_subtree(child_slug, depth + 1))
            return result

        tree = build_subtree(root_slug, 0)
        tree["total_network_size"] = self._count_tree_nodes(tree)
        return tree

    def _count_tree_nodes(self, node: dict) -> int:
        count = 1
        for child in node.get("children", []):
            count += self._count_tree_nodes(child)
        return count

    # ═══ Conversion Funnel ════════════════════════════════════════════

    def get_conversion_funnel(self, issuer_slug: str) -> dict:
        """
        Full QR node conversion funnel:
        qr_scan → join_page_open → member_created → activation_selected →
        payment_completed → wallet_init_completed → hls_issued
        """
        slug = issuer_slug.replace(".helios", "")
        stages = [
            "qr_scan", "join_page_open", "member_created",
            "activation_selected", "payment_completed",
            "wallet_init_completed", "hls_issued"
        ]
        funnel = {}
        for stage in stages:
            count = self.db.query(func.count(NodeEvent.id)).filter(
                NodeEvent.issuer_slug == slug,
                NodeEvent.event_type == stage,
                NodeEvent.status == "completed"
            ).scalar() or 0
            funnel[stage] = count

        return {
            "node": f"{slug}.helios",
            "funnel": funnel,
        }

    # ═══ Event History ════════════════════════════════════════════════

    def get_event_history(
        self, issuer_slug: str, limit: int = 50, event_type: str = None
    ) -> list:
        """Get recent events for a member node, newest first."""
        slug = issuer_slug.replace(".helios", "")
        query = self.db.query(NodeEvent).filter(
            NodeEvent.issuer_slug == slug
        )
        if event_type:
            query = query.filter(NodeEvent.event_type == event_type)
        events = query.order_by(NodeEvent.timestamp.desc()).limit(limit).all()
        return [e.to_dict() for e in events]

    # ═══ Chain Visualization Data ═════════════════════════════════════

    def get_chain_data(self, root_slug: str) -> dict:
        """
        Generate d3-compatible node/link data for chain visualization.
        Root at center, first-level direct recruits as ring,
        second-level branches extending, pulse for active nodes.
        """
        tree = self.get_propagation_tree(root_slug, max_depth=5)

        nodes = []
        links = []

        def walk(subtree, parent_id=None):
            member = subtree["member"]
            node_id = member.replace(".helios", "")
            depth = subtree["depth"]

            # Determine pulse (active in last 7 days)
            is_active = subtree.get("node_state") in ("connected", "propagating", "stable")

            nodes.append({
                "id": node_id,
                "label": member,
                "depth": depth,
                "state": subtree.get("node_state", "instantiated"),
                "bonds": subtree.get("bond_count", 0),
                "active": is_active,
                "group": min(depth, 4),  # for d3 color grouping
            })

            if parent_id:
                links.append({
                    "source": parent_id,
                    "target": node_id,
                    "depth": depth,
                })

            for child in subtree.get("children", []):
                walk(child, node_id)

        walk(tree)

        return {
            "root": root_slug.replace(".helios", ""),
            "total_nodes": len(nodes),
            "nodes": nodes,
            "links": links,
        }

    # ═══ Network-Wide Stats ═══════════════════════════════════════════

    def get_network_stats(self) -> dict:
        """Global network stats across all member nodes."""
        total_events = self.db.query(func.count(NodeEvent.id)).scalar() or 0
        total_scans = self.db.query(func.count(NodeEvent.id)).filter(
            NodeEvent.event_type.in_(["qr_scan", "qr_view", "card_view", "drop_view"])
        ).scalar() or 0
        total_joins = self.db.query(func.count(NodeEvent.id)).filter(
            NodeEvent.event_type == "member_created"
        ).scalar() or 0
        total_revenue = self.db.query(func.coalesce(func.sum(NodeEvent.amount_paid), 0)).filter(
            NodeEvent.event_type == "payment_completed"
        ).scalar() or 0.0
        total_hls = self.db.query(func.coalesce(func.sum(NodeEvent.hls_amount), 0)).filter(
            NodeEvent.event_type == "hls_issued"
        ).scalar() or 0.0

        # Top nodes by joins
        top_nodes = self.db.query(
            NodeEvent.issuer_slug,
            func.count(NodeEvent.id).label("count")
        ).filter(
            NodeEvent.event_type == "member_created"
        ).group_by(NodeEvent.issuer_slug).order_by(
            func.count(NodeEvent.id).desc()
        ).limit(10).all()

        return {
            "total_events": total_events,
            "total_scans": total_scans,
            "total_joins": total_joins,
            "total_revenue": round(total_revenue, 2),
            "total_hls_issued": round(total_hls, 2),
            "conversion_rate": round(total_joins / total_scans * 100, 1) if total_scans > 0 else 0.0,
            "top_nodes": [{"node": f"{r[0]}.helios", "joins": r[1]} for r in top_nodes],
        }
