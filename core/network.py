"""
Helios Neural Field Engine
═══════════════════════════════════════════════════
Undirected bounded graph. Max degree = 5 bonds per node.
No above. No below. Only connected peers inside a bounded field.
Settlement follows rules, not relationships.
"""

from datetime import datetime, timezone, timedelta
from collections import deque
from config import HeliosConfig


class FieldEngine:
    """
    Manages the Helios neural field — an undirected bounded graph.
    Each node can hold at most 5 bonds. Energy propagates through bonds
    using distance-based attenuation: weight(hop) = 1/(2^hop).
    """

    def __init__(self, db_session):
        self.db = db_session

    # ═══ Bond Formation ═══════════════════════════════════════════════
    def form_bond(self, initiator_id: str, peer_id: str) -> dict:
        """
        Create a bond between two nodes.
        Bonds are UNDIRECTED — there is no hierarchy.
        Both nodes must be active. Neither can be saturated (5 bonds).
        """
        from models.member import Member
        from models.bond import Bond

        # Validate both exist and are active
        initiator = self.db.query(Member).filter_by(
            helios_id=initiator_id, status="active"
        ).first()
        peer = self.db.query(Member).filter_by(
            helios_id=peer_id, status="active"
        ).first()

        if not initiator:
            raise ValueError(f"Node '{initiator_id}' not found in the field.")
        if not peer:
            raise ValueError(f"Node '{peer_id}' not found in the field.")
        if initiator_id == peer_id:
            raise ValueError("A node cannot bond with itself.")

        # Check saturation — max 5 bonds per node
        if initiator.bond_count >= HeliosConfig.FIELD_MAX_BONDS:
            raise ValueError(
                f"Node '{initiator_id}' has reached maximum bond capacity "
                f"({HeliosConfig.FIELD_MAX_BONDS}). Fully saturated."
            )
        if peer.bond_count >= HeliosConfig.FIELD_MAX_BONDS:
            raise ValueError(
                f"Node '{peer_id}' has reached maximum bond capacity "
                f"({HeliosConfig.FIELD_MAX_BONDS}). Fully saturated."
            )

        # Normalize pair (undirected — always store lower ID first)
        node_a, node_b = Bond.ordered_pair(initiator_id, peer_id)

        # Check for existing bond
        existing = self.db.query(Bond).filter_by(
            node_a=node_a, node_b=node_b
        ).first()
        if existing:
            if existing.state == HeliosConfig.BOND_STATE_ACTIVE:
                raise ValueError("Bond already active between these nodes.")
            if existing.state == HeliosConfig.BOND_STATE_INACTIVE:
                # Reactivate dormant bond
                existing.state = HeliosConfig.BOND_STATE_ACTIVE
                existing.activated_at = datetime.now(timezone.utc)
                existing.deactivated_at = None
                initiator.bond_count += 1
                peer.bond_count += 1
                initiator.update_node_state()
                peer.update_node_state()
                self.db.commit()
                return {
                    "reactivated": True,
                    "bond_id": existing.id,
                    "nodes": [initiator_id, peer_id],
                    "message": f"Bond reactivated between {initiator_id} and {peer_id}."
                }

        # Create bond
        bond = Bond(
            node_a=node_a,
            node_b=node_b,
            state=HeliosConfig.BOND_STATE_ACTIVE,
            initiated_by=initiator_id,
            created_at=datetime.now(timezone.utc),
            activated_at=datetime.now(timezone.utc)
        )
        self.db.add(bond)

        # Update bond counts and node states
        initiator.bond_count += 1
        peer.bond_count += 1
        initiator.update_node_state()
        peer.update_node_state()

        self.db.commit()

        return {
            "bonded": True,
            "bond_id": bond.id,
            "nodes": [initiator_id, peer_id],
            "initiator_state": initiator.node_state,
            "peer_state": peer.node_state,
            "message": f"Bond formed between {initiator_id} and {peer_id}."
        }

    def dissolve_bond(self, node_id: str, peer_id: str) -> dict:
        """Deactivate a bond. History is permanent — state changes to INACTIVE."""
        from models.member import Member
        from models.bond import Bond

        node_a, node_b = Bond.ordered_pair(node_id, peer_id)
        bond = self.db.query(Bond).filter_by(
            node_a=node_a, node_b=node_b, state=HeliosConfig.BOND_STATE_ACTIVE
        ).first()

        if not bond:
            raise ValueError("No active bond found between these nodes.")

        bond.state = HeliosConfig.BOND_STATE_INACTIVE
        bond.deactivated_at = datetime.now(timezone.utc)

        # Update bond counts
        node = self.db.query(Member).filter_by(helios_id=node_id).first()
        peer = self.db.query(Member).filter_by(helios_id=peer_id).first()
        if node:
            node.bond_count = max(0, node.bond_count - 1)
            node.update_node_state()
        if peer:
            peer.bond_count = max(0, peer.bond_count - 1)
            peer.update_node_state()

        self.db.commit()
        return {"dissolved": True, "message": "Bond deactivated."}

    # ═══ Field Traversal (BFS — Undirected Graph) ═════════════════════
    def get_field(self, helios_id: str, max_hops: int = None) -> dict:
        """
        Traverse the neural field from a node outward.
        Returns all reachable nodes and bonds within max_hops.
        No hierarchy — just distance from the origin node.
        """
        if max_hops is None:
            max_hops = min(HeliosConfig.PROPAGATION_MAX_HOPS, 6)  # Viz default

        from models.bond import Bond
        from models.member import Member

        visited = {}  # helios_id → hop distance
        nodes = []
        edges = []
        queue = deque([(helios_id, 0)])
        visited[helios_id] = 0

        while queue:
            current_id, hops = queue.popleft()
            if hops > max_hops:
                continue

            # Get node info
            member = self.db.query(Member).filter_by(helios_id=current_id).first()
            if member:
                nodes.append({
                    "id": current_id,
                    "name": member.display_name,
                    "hops": hops,
                    "node_state": member.node_state,
                    "bond_count": member.bond_count,
                    "activity": self._get_activity_score(current_id),
                    "is_origin": current_id == helios_id,
                    "energy_weight": 1.0 / (HeliosConfig.PROPAGATION_DECAY_BASE ** hops) if hops > 0 else 1.0
                })

            # Get all active bonds for this node (undirected)
            bonds = self.db.query(Bond).filter(
                ((Bond.node_a == current_id) | (Bond.node_b == current_id)),
                Bond.state == HeliosConfig.BOND_STATE_ACTIVE
            ).all()

            for bond in bonds:
                peer_id = bond.peer_of(current_id)
                edge_key = tuple(sorted([current_id, peer_id]))

                # Add edge (deduplicated)
                if not any(e["key"] == edge_key for e in edges):
                    edges.append({
                        "source": current_id,
                        "target": peer_id,
                        "key": edge_key,
                        "state": bond.state,
                        "since": bond.created_at.isoformat()
                    })

                # Traverse to peer if not visited and within range
                if peer_id not in visited and hops + 1 <= max_hops:
                    visited[peer_id] = hops + 1
                    queue.append((peer_id, hops + 1))

        return {
            "origin": helios_id,
            "max_hops": max_hops,
            "total_nodes": len(nodes),
            "total_bonds": len(edges),
            "nodes": nodes,
            "edges": edges
        }

    def get_bonds(self, helios_id: str) -> list:
        """Get all active bonds for a node — its direct peers."""
        from models.bond import Bond
        from models.member import Member

        bonds = self.db.query(Bond).filter(
            ((Bond.node_a == helios_id) | (Bond.node_b == helios_id)),
            Bond.state == HeliosConfig.BOND_STATE_ACTIVE
        ).all()

        result = []
        for bond in bonds:
            peer_id = bond.peer_of(helios_id)
            peer = self.db.query(Member).filter_by(helios_id=peer_id).first()
            if peer:
                result.append({
                    "helios_id": peer_id,
                    "name": peer.display_name,
                    "node_state": peer.node_state,
                    "bond_since": bond.created_at.isoformat(),
                    "activity": self._get_activity_score(peer_id)
                })

        return result

    def get_propagation_path(self, from_id: str, to_id: str) -> dict:
        """Find shortest path between two nodes via BFS. Used for settlement routing."""
        from models.bond import Bond

        if from_id == to_id:
            return {"path": [from_id], "hops": 0}

        visited = {from_id: None}
        queue = deque([from_id])

        while queue:
            current = queue.popleft()

            bonds = self.db.query(Bond).filter(
                ((Bond.node_a == current) | (Bond.node_b == current)),
                Bond.state == HeliosConfig.BOND_STATE_ACTIVE
            ).all()

            for bond in bonds:
                peer = bond.peer_of(current)
                if peer not in visited:
                    visited[peer] = current
                    if peer == to_id:
                        # Reconstruct path
                        path = [to_id]
                        node = to_id
                        while visited[node] is not None:
                            node = visited[node]
                            path.append(node)
                        path.reverse()
                        return {"path": path, "hops": len(path) - 1}
                    queue.append(peer)

        return {"path": [], "hops": -1, "message": "No path exists between these nodes."}

    # ═══ Field Statistics ═════════════════════════════════════════════
    def get_node_stats(self, helios_id: str) -> dict:
        """Comprehensive node statistics within the field."""
        from models.member import Member

        member = self.db.query(Member).filter_by(helios_id=helios_id).first()
        if not member:
            raise ValueError(f"Node '{helios_id}' not found.")

        bonds = self.get_bonds(helios_id)
        field = self.get_field(helios_id, max_hops=5)

        # Bond capacity
        capacity = member.bond_count / HeliosConfig.FIELD_MAX_BONDS * 100

        # Field reach at different distances
        hop_distribution = {}
        for node in field["nodes"]:
            h = node["hops"]
            if h not in hop_distribution:
                hop_distribution[h] = 0
            hop_distribution[h] += 1

        return {
            "helios_id": helios_id,
            "node_state": member.node_state,
            "bond_count": member.bond_count,
            "bond_capacity": f"{capacity:.0f}%",
            "max_bonds": HeliosConfig.FIELD_MAX_BONDS,
            "direct_peers": len(bonds),
            "field_reach_5_hops": field["total_nodes"],
            "activity_score": self._get_activity_score(helios_id),
            "hop_distribution": hop_distribution,
            "field_health": self._calculate_field_health(field)
        }

    # ═══ Activity Measurement ═════════════════════════════════════════
    def record_activity(self, helios_id: str, activity_type: str,
                        value: float = 1.0, extra_data: dict = None) -> dict:
        """Record any field activity: bond, transaction, engagement, verification."""
        from models.transaction import Transaction

        valid_types = ["bond", "transaction", "engagement", "verification", "propagation"]
        if activity_type not in valid_types:
            raise ValueError(f"Activity type must be one of: {valid_types}")

        txn = Transaction(
            member_id=helios_id,
            activity_type=activity_type,
            value=value,
            extra_data=extra_data or {},
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(txn)
        self.db.commit()

        return {
            "recorded": True,
            "transaction_id": txn.id,
            "activity_type": activity_type,
            "new_score": self._get_activity_score(helios_id)
        }

    # ═══ Internal Helpers ═════════════════════════════════════════════
    def _get_activity_score(self, helios_id: str) -> float:
        """Activity score for the rolling window."""
        from models.transaction import Transaction
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=HeliosConfig.FIELD_ACTIVITY_WINDOW_DAYS
        )
        count = self.db.query(Transaction).filter(
            Transaction.member_id == helios_id,
            Transaction.created_at >= cutoff
        ).count()
        return min(round(count / HeliosConfig.FIELD_ACTIVITY_WINDOW_DAYS * 100, 1), 100.0)

    def _calculate_field_health(self, field: dict) -> str:
        """Field health based on node activity distribution."""
        if not field["nodes"]:
            return "new"

        active = sum(1 for n in field["nodes"] if n["activity"] > 0)
        ratio = active / len(field["nodes"]) if field["nodes"] else 0

        if ratio >= 0.7:
            return "excellent"
        elif ratio >= 0.4:
            return "healthy"
        elif ratio >= 0.2:
            return "growing"
        else:
            return "emerging"
