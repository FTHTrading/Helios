"""Bond model — undirected peer bonds in the neural field.

Bonds are UNDIRECTED. node_a and node_b are peers. The lower helios_id is
always node_a to prevent duplicate bonds (A→B and B→A are the same bond).

Bond State Machine: PENDING → ACTIVE → INACTIVE
                                  └──→ DISPUTED
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, UniqueConstraint
from models.member import Base


class Bond(Base):
    __tablename__ = "bonds"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Undirected: node_a < node_b (lexicographic) to prevent duplicates
    node_a = Column(String(64), nullable=False, index=True)
    node_b = Column(String(64), nullable=False, index=True)

    # Bond state machine: pending → active → inactive / disputed
    state = Column(String(20), default="pending", index=True)

    # Who initiated the bond
    initiated_by = Column(String(64), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    activated_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)

    # Ensure no duplicate bonds between same pair
    __table_args__ = (
        UniqueConstraint('node_a', 'node_b', name='uq_bond_pair'),
    )

    # Valid states
    VALID_STATES = ("pending", "active", "inactive", "disputed")

    def __repr__(self):
        return f"<Bond {self.node_a} ⟷ {self.node_b} [{self.state}]>"

    @staticmethod
    def ordered_pair(id_1: str, id_2: str) -> tuple:
        """Always return (smaller, larger) to enforce undirected consistency."""
        return (id_1, id_2) if id_1 < id_2 else (id_2, id_1)

    def involves(self, helios_id: str) -> bool:
        """Check if this bond involves a given node."""
        return self.node_a == helios_id or self.node_b == helios_id

    def peer_of(self, helios_id: str) -> str:
        """Get the other node in this bond."""
        if self.node_a == helios_id:
            return self.node_b
        elif self.node_b == helios_id:
            return self.node_a
        raise ValueError(f"{helios_id} is not part of this bond")
