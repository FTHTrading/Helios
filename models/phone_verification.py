"""
PhoneVerification — DB-backed SMS verification codes.
═══════════════════════════════════════════════════════════════════════
Replaces the in-memory dict so codes survive restarts and
work across multiple worker processes.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from models.member import Base


class PhoneVerification(Base):
    __tablename__ = "phone_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    verification_id = Column(String(64), unique=True, nullable=False, index=True)
    phone_hash = Column(String(128), nullable=False, index=True)
    code_hash = Column(String(128), nullable=False)
    helios_id = Column(String(64), nullable=True, index=True)

    attempts = Column(Integer, default=0)
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<PhoneVerification {self.verification_id} [{'verified' if self.verified else 'pending'}]>"
