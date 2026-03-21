"""Link model — bidirectional peer connections in the neural field.

Links are UNDIRECTED. There is no "from" or "to" in hierarchical terms.
node_a and node_b are peers. The lower helios_id is always node_a
to prevent duplicate links (A→B and B→A are the same link).

Link State Machine: DISCOVER → BOUND → ACTIVE → INACTIVE
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, UniqueConstraint
from models.member import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Undirected: node_a < node_b (lexicographic) to prevent duplicates
    node_a = Column(String(64), nullable=False, index=True)
    node_b = Column(String(64), nullable=False, index=True)

    # Link state machine
    state = Column(String(20), default="bound", index=True)

    # Who initiated the link (for acknowledgement tracking)
    initiated_by = Column(String(64), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)

    # Ensure no duplicate links between same pair
    __table_args__ = (
        UniqueConstraint('node_a', 'node_b', name='uq_link_pair'),
    )

    def __repr__(self):
        return f"<Link {self.node_a} ⟷ {self.node_b} [{self.state}]>"

    @staticmethod
    def ordered_pair(id_1: str, id_2: str) -> tuple:
        """Always return (smaller, larger) to enforce undirected consistency."""
        return (id_1, id_2) if id_1 < id_2 else (id_2, id_1)

    def involves(self, helios_id: str) -> bool:
        """Check if this link involves a given node."""
        return self.node_a == helios_id or self.node_b == helios_id

    def peer_of(self, helios_id: str) -> str:
        """Get the other node in this link."""
        if self.node_a == helios_id:
            return self.node_b
        elif self.node_b == helios_id:
            return self.node_a
        raise ValueError(f"{helios_id} is not part of this link")
