"""Member model — every node in the Helios neural field."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    helios_id = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(64), nullable=False)
    key_hash = Column(String(128), nullable=False)
    recovery_hash = Column(String(128), nullable=False)
    referrer_id = Column(String(64), nullable=True, index=True)  # initiator — who introduced this node

    # ═══ Node State Machine ═══
    # INSTANTIATED → ACKNOWLEDGED → CONNECTED → PROPAGATING → STABLE
    node_state = Column(String(20), default="instantiated", index=True)
    link_count = Column(Integer, default=0)  # Current number of active links

    status = Column(String(20), default="active", index=True)
    verified = Column(Boolean, default=False)
    email_hash = Column(String(128), nullable=True)
    phone_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Node {self.helios_id} [{self.node_state}]>"

    def to_dict(self):
        return {
            "helios_id": self.helios_id,
            "display_name": self.display_name,
            "initiator": self.referrer_id,
            "node_state": self.node_state,
            "link_count": self.link_count,
            "status": self.status,
            "verified": self.verified,
            "member_since": self.created_at.isoformat() if self.created_at else None
        }

    def update_node_state(self):
        """Recalculate node state based on link count."""
        if self.link_count >= 5:
            self.node_state = "stable"
        elif self.link_count >= 3:
            self.node_state = "propagating"
        elif self.link_count >= 1:
            self.node_state = "connected"
        # acknowledged and instantiated are set during join flow
