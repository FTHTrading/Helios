"""
Helios Energy Propagation Engine
═══════════════════════════════════════════════════════════════
Settlement follows physics, not position.
Energy propagates outward from join events through the neural field.
Strongest at direct links, attenuates naturally: weight(hop) = 1/(2^hop).
After hop 15, fractional remainder absorbs into protocol stability pools.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_DOWN
from collections import deque
from config import HeliosConfig


class PropagationEngine:
    """
    Calculates and distributes energy through the neural field.
    Rules are FIXED. No admin overrides. Every settlement is verifiable.

    Join Event Flow:
    1. ACKNOWLEDGEMENT — one-time payment to the initiator
    2. PROPAGATION — energy radiates outward through links up to 15 hops
    3. ABSORPTION — fractional remainder after hop 15 enters protocol pools
    """

    def __init__(self, db_session):
        self.db = db_session

    # ═══ Core Settlement ══════════════════════════════════════════════
    def calculate_propagation(self, origin_id: str, energy_amount: Decimal,
                               event_type: str = "join") -> dict:
        """
        Calculate how energy propagates from an origin node through the field.
        Returns a full breakdown: acknowledgement + hop-by-hop distribution + absorption.
        """
        from models.member import Member
        from models.link import Link

        origin = self.db.query(Member).filter_by(
            helios_id=origin_id, status="active"
        ).first()
        if not origin:
            raise ValueError(f"Node '{origin_id}' not found in the field.")

        distributions = []
        total_propagated = Decimal('0')

        # ─── Phase 1: Acknowledgement (one-time, to initiator) ────────
        if event_type == "join" and origin.referrer_id:
            ack_amount = Decimal(str(HeliosConfig.ACKNOWLEDGEMENT_AMOUNT))
            initiator = self.db.query(Member).filter_by(
                helios_id=origin.referrer_id, status="active"
            ).first()

            if initiator and self._get_activity_score(initiator.helios_id) >= HeliosConfig.SETTLEMENT_MIN_ACTIVITY_SCORE:
                distributions.append({
                    "recipient": initiator.helios_id,
                    "amount": float(ack_amount),
                    "type": "acknowledgement",
                    "hop": 0,
                    "weight": 1.0,
                    "reason": f"Acknowledgement for initiating {origin_id}"
                })
                total_propagated += ack_amount
            else:
                # Initiator inactive — absorbed into stability pool
                distributions.append({
                    "recipient": "POOL:stability",
                    "amount": float(ack_amount),
                    "type": "absorption",
                    "hop": 0,
                    "weight": 1.0,
                    "reason": "Initiator inactive — absorbed into stability"
                })
                total_propagated += ack_amount

        # ─── Phase 2: Energy Propagation (BFS through links) ──────────
        propagation_energy = energy_amount - total_propagated
        if propagation_energy <= 0:
            propagation_energy = energy_amount  # For non-join events

        visited = {origin_id: 0}
        queue = deque([(origin_id, 0)])
        hop_distributions = []

        while queue:
            current_id, hop = queue.popleft()

            # Get active links from current node
            links = self.db.query(Link).filter(
                ((Link.node_a == current_id) | (Link.node_b == current_id)),
                Link.state == HeliosConfig.LINK_STATE_ACTIVE
            ).all()

            for link in links:
                peer_id = link.peer_of(current_id)
                next_hop = hop + 1

                if peer_id in visited:
                    continue  # Already reached via shorter path
                if next_hop > HeliosConfig.PROPAGATION_MAX_HOPS:
                    continue  # Beyond energy horizon

                visited[peer_id] = next_hop

                # Calculate energy weight: 1/(2^hop)
                weight = Decimal('1') / Decimal(str(HeliosConfig.PROPAGATION_DECAY_BASE ** next_hop))
                hop_amount = (propagation_energy * weight).quantize(
                    Decimal('0.00000001'), rounding=ROUND_DOWN
                )

                if hop_amount <= 0:
                    continue

                # Check if peer is active enough to receive energy
                peer_score = self._get_activity_score(peer_id)
                if peer_score >= HeliosConfig.SETTLEMENT_MIN_ACTIVITY_SCORE:
                    hop_distributions.append({
                        "recipient": peer_id,
                        "amount": float(hop_amount),
                        "type": "propagation",
                        "hop": next_hop,
                        "weight": float(weight),
                        "reason": f"Energy propagation at hop {next_hop}"
                    })
                else:
                    hop_distributions.append({
                        "recipient": "POOL:stability",
                        "amount": float(hop_amount),
                        "type": "absorption",
                        "hop": next_hop,
                        "weight": float(weight),
                        "reason": f"Inactive node at hop {next_hop} — absorbed"
                    })

                total_propagated += hop_amount
                queue.append((peer_id, next_hop))

        distributions.extend(hop_distributions)

        # ─── Phase 3: Absorption (fractional remainder) ───────────────
        remainder = energy_amount - total_propagated
        if remainder > 0:
            absorption = self._calculate_absorption(remainder)
            distributions.extend(absorption)
            total_propagated += remainder

        return {
            "origin": origin_id,
            "event_type": event_type,
            "energy_input": float(energy_amount),
            "total_propagated": float(total_propagated),
            "distribution_count": len(distributions),
            "max_hop_reached": max((d["hop"] for d in distributions), default=0),
            "distributions": distributions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verifiable": True
        }

    def execute_propagation(self, origin_id: str, energy_amount: Decimal,
                             event_type: str = "join") -> dict:
        """Calculate AND execute the propagation — record all settlements."""
        from models.reward import Reward

        calc = self.calculate_propagation(origin_id, energy_amount, event_type)

        # Record each distribution
        reward_records = []
        for dist in calc["distributions"]:
            reward = Reward(
                member_id=dist["recipient"],
                source_member_id=origin_id,
                amount=dist["amount"],
                reward_type=dist["type"],
                activity_type=event_type,
                reason=dist["reason"],
                created_at=datetime.now(timezone.utc),
                status="settled"
            )
            self.db.add(reward)
            reward_records.append(reward)

        self.db.commit()

        calc["executed"] = True
        calc["settlement_ids"] = [r.id for r in reward_records]
        return calc

    # ═══ Absorption Pool Distribution ═════════════════════════════════
    def _calculate_absorption(self, remainder: Decimal) -> list:
        """
        Split fractional remainder into protocol pools.
        Stability 40% | Liquidity 25% | Intelligence 20% | Compliance 15%
        """
        pools = [
            ("POOL:stability", HeliosConfig.ABSORPTION_STABILITY_PERCENT),
            ("POOL:liquidity", HeliosConfig.ABSORPTION_LIQUIDITY_PERCENT),
            ("POOL:intelligence", HeliosConfig.ABSORPTION_INTELLIGENCE_PERCENT),
            ("POOL:compliance", HeliosConfig.ABSORPTION_COMPLIANCE_PERCENT),
        ]

        distributions = []
        distributed = Decimal('0')

        for pool_name, percent in pools:
            amount = (remainder * Decimal(str(percent)) / Decimal('100')).quantize(
                Decimal('0.00000001'), rounding=ROUND_DOWN
            )
            distributions.append({
                "recipient": pool_name,
                "amount": float(amount),
                "type": "absorption",
                "hop": -1,
                "weight": 0,
                "reason": f"Fractional absorption — {pool_name.split(':')[1]}"
            })
            distributed += amount

        # Dust goes to stability
        dust = remainder - distributed
        if dust > 0:
            distributions[0]["amount"] = float(Decimal(str(distributions[0]["amount"])) + dust)

        return distributions

    # ═══ Queries ══════════════════════════════════════════════════════
    def get_settlement_history(self, helios_id: str, limit: int = 50) -> list:
        """Get settlement history for a node."""
        from models.reward import Reward

        rewards = self.db.query(Reward).filter_by(
            member_id=helios_id
        ).order_by(Reward.created_at.desc()).limit(limit).all()

        return [{
            "id": r.id,
            "amount": r.amount,
            "type": r.reward_type,
            "source": r.source_member_id,
            "reason": r.reason,
            "date": r.created_at.isoformat(),
            "status": r.status
        } for r in rewards]

    def get_total_energy_received(self, helios_id: str) -> dict:
        """Total energy received, broken down by type."""
        from models.reward import Reward
        from sqlalchemy import func

        results = self.db.query(
            Reward.reward_type,
            func.sum(Reward.amount).label("total"),
            func.count(Reward.id).label("count")
        ).filter_by(
            member_id=helios_id, status="settled"
        ).group_by(Reward.reward_type).all()

        breakdown = {}
        grand_total = 0
        for reward_type, total, count in results:
            breakdown[reward_type] = {
                "total": float(total),
                "count": count
            }
            grand_total += float(total)

        return {
            "node": helios_id,
            "total_energy": grand_total,
            "breakdown": breakdown,
            "token": HeliosConfig.TOKEN_SYMBOL
        }

    def get_protocol_stats(self) -> dict:
        """Public protocol statistics — anyone can verify."""
        from models.reward import Reward
        from sqlalchemy import func

        total_distributed = self.db.query(
            func.sum(Reward.amount)
        ).filter(
            Reward.status == "settled",
            ~Reward.member_id.startswith("POOL")
        ).scalar() or 0

        pool_balance = self.db.query(
            func.sum(Reward.amount)
        ).filter(
            Reward.status == "settled",
            Reward.member_id.startswith("POOL")
        ).scalar() or 0

        pool_max = HeliosConfig.TOKEN_TOTAL_SUPPLY * HeliosConfig.TOKEN_POOL_LOCK_PERCENT / 100

        return {
            "pool_balance": float(pool_balance),
            "pool_max": pool_max,
            "pool_utilization": round(float(pool_balance) / pool_max * 100, 2) if pool_max > 0 else 0,
            "total_propagated_to_nodes": float(total_distributed),
            "token": HeliosConfig.TOKEN_SYMBOL,
            "protocol_rules": {
                "max_links_per_node": HeliosConfig.FIELD_MAX_LINKS,
                "propagation_hops": HeliosConfig.PROPAGATION_MAX_HOPS,
                "decay_function": f"1/(2^hop)",
                "acknowledgement": f"{HeliosConfig.ACKNOWLEDGEMENT_AMOUNT} HLS",
                "absorption_split": {
                    "stability": f"{HeliosConfig.ABSORPTION_STABILITY_PERCENT}%",
                    "liquidity": f"{HeliosConfig.ABSORPTION_LIQUIDITY_PERCENT}%",
                    "intelligence": f"{HeliosConfig.ABSORPTION_INTELLIGENCE_PERCENT}%",
                    "compliance": f"{HeliosConfig.ABSORPTION_COMPLIANCE_PERCENT}%",
                },
                "min_activity_score": HeliosConfig.SETTLEMENT_MIN_ACTIVITY_SCORE
            }
        }

    # ═══ Helpers ══════════════════════════════════════════════════════
    def _get_activity_score(self, helios_id: str) -> float:
        """Activity score for settlement qualification."""
        from models.transaction import Transaction
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=HeliosConfig.FIELD_ACTIVITY_WINDOW_DAYS
        )
        count = self.db.query(Transaction).filter(
            Transaction.member_id == helios_id,
            Transaction.created_at >= cutoff
        ).count()
        return min(round(count / HeliosConfig.FIELD_ACTIVITY_WINDOW_DAYS * 100, 1), 100.0)
