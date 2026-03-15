"""Reward model — every payout, fully auditable ledger."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON
from models.member import Base


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(64), nullable=False, index=True)
    source_member_id = Column(String(64), nullable=True)
    amount = Column(Float, nullable=False)
    reward_type = Column(String(40), nullable=False, index=True)
    activity_type = Column(String(30), nullable=True)
    reason = Column(String(280), nullable=True)
    status = Column(String(20), default="settled", index=True)

    # ═══ Ledger / Audit Fields ═══
    tx_hash = Column(String(128), nullable=True)              # On-chain settlement tx hash
    settlement_chain = Column(String(30), nullable=True)      # xrpl, stellar, internal
    proof_hash = Column(String(128), nullable=True)           # Deterministic hash of this entry
    ledger_entry_type = Column(String(30), default="credit")  # credit, debit, adjustment
    node_event_id = Column(Integer, nullable=True, index=True) # FK to node_events.id
    hop_depth = Column(Integer, nullable=True)                # Propagation hop if applicable
    pool_source = Column(String(40), nullable=True)           # Which pool funded this reward
    batch_id = Column(String(64), nullable=True)              # Settlement batch grouping
    notes = Column(Text, nullable=True)                       # Operator/system notes
    extra = Column(JSON, nullable=True)                       # Extensible payload

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Reward {self.member_id} | {self.amount} HLS | {self.ledger_entry_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "source_member_id": self.source_member_id,
            "amount": self.amount,
            "reward_type": self.reward_type,
            "activity_type": self.activity_type,
            "reason": self.reason,
            "status": self.status,
            "tx_hash": self.tx_hash,
            "settlement_chain": self.settlement_chain,
            "proof_hash": self.proof_hash,
            "ledger_entry_type": self.ledger_entry_type,
            "node_event_id": self.node_event_id,
            "hop_depth": self.hop_depth,
            "pool_source": self.pool_source,
            "batch_id": self.batch_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
