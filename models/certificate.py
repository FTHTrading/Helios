"""
Helios Certificate (HC-NFT) - Key-Bound Stored Energy Battery.
===============================================================
Cryptographically addressed. Key-bound. Meaning-free on chain.
Rich inside HELIOS.

certificate_id = HC-{SHA256(holder_key + energy_amount + epoch + rate)[:24]}

State Machine: ACTIVE -> REDEEMED   (gold or stablecoin exit)
               ACTIVE -> CANCELLED  (2% energy burned permanently - irreversible)
"""

import hashlib
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean
from models.member import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # === Identity - Cryptographically Addressed ===
    certificate_id = Column(String(64), unique=True, nullable=False, index=True)  # HC-{sha256[:24]}
    content_hash = Column(String(64), nullable=True, index=True)      # Full SHA256 of payload
    holder_id = Column(String(64), nullable=False, index=True)        # Key of holder

    # === Energy Stored ===
    energy_amount_he = Column(Float, nullable=False)                 # HE stored in this certificate
    energy_value_usd = Column(Float, nullable=False)                 # USD equivalent at mint time
    mint_rate = Column(Float, nullable=False)                        # HE/USD rate at mint

    # === State Machine ===
    state = Column(String(20), default="active", index=True)         # active, redeemed, cancelled

    # === Redemption Details (populated on redeem/cancel) ===
    redemption_type = Column(String(20), nullable=True)              # GOLD, STABLECOIN, CANCEL
    redemption_amount = Column(Float, nullable=True)                 # Amount received
    friction_paid = Column(Float, nullable=True)                     # 2% friction on cancel
    redeemed_at = Column(DateTime, nullable=True)

    # === Backing ===
    linked_mvr_id = Column(String(64), nullable=True, index=True)   # MVR backing gold redemption
    notes = Column(Text, nullable=True)

    # === Finality (cancellation is irreversible) ===
    is_final = Column(Boolean, default=False)                        # True once cancelled/redeemed
    energy_burned_he = Column(Float, nullable=True)                  # Permanent burn on cancel

    # === IPFS / On-chain metadata ===
    ipfs_cid = Column(String(128), nullable=True, index=True)         # Pinata CID after pinning
    metadata_pinned = Column(Boolean, default=False)                  # True once pinned to IPFS
    chain_rail = Column(String(16), default="XRPL")                   # XRPL | EVM

    # === Timestamps ===
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        h = self.content_hash[:12] if self.content_hash else "none"
        return f"<HC-NFT {self.certificate_id} | {self.energy_amount_he} HE [{self.state}] hash={h}>"

    def to_dict(self):
        return {
            "certificate_id": self.certificate_id,
            "content_hash": self.content_hash,
            "holder_id": self.holder_id,
            "energy_amount_he": self.energy_amount_he,
            "energy_value_usd": self.energy_value_usd,
            "state": self.state,
            "is_final": self.is_final,
            "redemption_type": self.redemption_type,
            "redemption_amount": self.redemption_amount,
            "friction_paid": self.friction_paid,
            "energy_burned_he": self.energy_burned_he,
            "linked_mvr_id": self.linked_mvr_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "redeemed_at": self.redeemed_at.isoformat() if self.redeemed_at else None,
        }

    @property
    def is_active(self):
        return self.state == "active"

    @property
    def cancel_friction_amount(self):
        """2% friction if cancelled."""
        from config import HeliosConfig
        return self.energy_value_usd * HeliosConfig.CERTIFICATE_CANCEL_FRICTION

    @staticmethod
    def compute_certificate_hash(holder_id: str, energy_amount_he: float,
                                  epoch_timestamp: int, mint_rate: float) -> str:
        """Deterministic SHA256: key + amount + timestamp + rate."""
        payload = f"{holder_id}|{energy_amount_he:.8f}|{epoch_timestamp}|{mint_rate:.8f}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def generate_certificate_id(content_hash: str) -> str:
        """HC-{first 24 chars of SHA256} - deterministic, addressable."""
        return f"HC-{content_hash[:24].upper()}"
