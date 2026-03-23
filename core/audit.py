"""
core/audit.py — Audit Trail for Helios Protocol
=================================================
Structured audit logging for all critical operations:
  - Token minting (XRPL + EVM)
  - NFT minting
  - Settlement propagation
  - Treasury operations
  - Certificate lifecycle
  - Admin actions

All audit events are:
  1. Written to the database (audit_log table)
  2. Emitted to structured logging
  3. Optionally pushed to Sentry breadcrumbs
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, String, DateTime, Integer, Text, Float
from models.member import Base

log = logging.getLogger("helios.audit")


class AuditAction(str, Enum):
    """Enumeration of auditable actions."""
    TOKEN_MINT_XRPL = "token_mint_xrpl"
    TOKEN_MINT_EVM = "token_mint_evm"
    NFT_MINT = "nft_mint"
    CEREMONIAL_MINT = "ceremonial_mint"
    SETTLEMENT_START = "settlement_start"
    SETTLEMENT_COMPLETE = "settlement_complete"
    SETTLEMENT_FAILED = "settlement_failed"
    CERTIFICATE_CREATE = "certificate_create"
    CERTIFICATE_REDEEM = "certificate_redeem"
    CERTIFICATE_CANCEL = "certificate_cancel"
    TREASURY_ANCHOR = "treasury_anchor"
    IPFS_PIN = "ipfs_pin"
    MEMBER_JOIN = "member_join"
    ADMIN_ACTION = "admin_action"
    CONFIG_CHANGE = "config_change"
    AUTH_FAILURE = "auth_failure"


class AuditLog(Base):
    """Persistent audit trail stored in the database."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(64), nullable=False, index=True)
    actor_id = Column(String(128), nullable=True, index=True)     # member_id or "system"
    target_id = Column(String(128), nullable=True, index=True)    # affected entity
    chain = Column(String(16), nullable=True)                      # XRPL | EVM | None
    tx_hash = Column(String(128), nullable=True, index=True)
    amount = Column(Float, nullable=True)
    detail = Column(Text, nullable=True)                           # JSON-serialized context
    idempotency_key = Column(String(64), nullable=True, unique=True, index=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<Audit {self.action} actor={self.actor_id} at={self.created_at}>"

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "chain": self.chain,
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "detail": json.loads(self.detail) if self.detail else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def record_audit(session, action: AuditAction | str, *,
                 actor_id: str = "system",
                 target_id: str = None,
                 chain: str = None,
                 tx_hash: str = None,
                 amount: float = None,
                 detail: dict = None,
                 idempotency_key: str = None,
                 ip_address: str = None) -> AuditLog | None:
    """
    Record an audit event to both the database and structured logs.

    Uses idempotency_key to prevent duplicate records (replay protection).
    Returns the AuditLog entry on success, None if duplicate.
    """
    action_str = action.value if isinstance(action, AuditAction) else str(action)

    # Replay protection via idempotency key
    if idempotency_key:
        existing = session.query(AuditLog).filter_by(
            idempotency_key=idempotency_key
        ).first()
        if existing:
            log.debug("Audit replay blocked: %s (key=%s)", action_str, idempotency_key)
            return None

    entry = AuditLog(
        action=action_str,
        actor_id=actor_id,
        target_id=target_id,
        chain=chain,
        tx_hash=tx_hash,
        amount=amount,
        detail=json.dumps(detail, default=str) if detail else None,
        idempotency_key=idempotency_key,
        ip_address=ip_address,
    )

    try:
        session.add(entry)
        session.commit()
    except Exception:
        session.rollback()
        log.error("Failed to write audit record: %s", action_str, exc_info=True)
        return None

    # Structured log emission
    log.info(
        "AUDIT action=%s actor=%s target=%s chain=%s tx=%s amount=%s",
        action_str,
        actor_id,
        target_id or "-",
        chain or "-",
        (tx_hash[:16] + "...") if tx_hash and len(tx_hash) > 16 else (tx_hash or "-"),
        amount or "-",
    )

    # Sentry breadcrumb (if SDK is loaded)
    try:
        import sentry_sdk
        sentry_sdk.add_breadcrumb(
            category="audit",
            message=f"{action_str}: {actor_id} → {target_id or 'n/a'}",
            level="info",
            data={"chain": chain, "tx_hash": tx_hash, "amount": amount},
        )
    except Exception:
        pass

    return entry


def generate_idempotency_key(*parts) -> str:
    """Generate a deterministic idempotency key from parts."""
    payload = "|".join(str(p) for p in parts)
    return hashlib.sha256(payload.encode()).hexdigest()[:48]
