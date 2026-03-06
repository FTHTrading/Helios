"""Payment event model — checkout sessions and webhook fulfillment history."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, JSON
from models.member import Base


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(128), unique=True, nullable=False, index=True)
    reference_id = Column(String(128), nullable=True, index=True)
    provider = Column(String(32), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    member_id = Column(String(64), nullable=True, index=True)
    offer_code = Column(String(64), nullable=True, index=True)
    mode = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default="created", index=True)
    currency = Column(String(8), nullable=True, default="usd")
    amount_usd = Column(Float, default=0.0)
    raw_payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "external_id": self.external_id,
            "reference_id": self.reference_id,
            "provider": self.provider,
            "event_type": self.event_type,
            "member_id": self.member_id,
            "offer_code": self.offer_code,
            "mode": self.mode,
            "status": self.status,
            "currency": self.currency,
            "amount_usd": self.amount_usd,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
