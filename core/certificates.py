"""
Certificate Engine - HC-NFT Lifecycle
===================================================================
Key-bound, cryptographically addressed. Meaning-free on chain.
Rich inside HELIOS.

certificate_id = HC-{SHA256(holder_key + amount + epoch + rate)[:24]}

State Machine: ACTIVE -> REDEEMED   (gold/stablecoin exit, gated by RRR covenant)
               ACTIVE -> CANCELLED  (2% energy burned permanently - irreversible)

RRR Covenant: Reserve Ratio < 1.0 = auto-pause redemptions. No override.
"""

import hashlib
import time
from datetime import datetime, timezone
from config import HeliosConfig
from models.certificate import Certificate
from models.member import Member


class CertificateEngine:
    """Stored energy batteries. Every certificate is cryptographically addressed."""

    def __init__(self, db_session):
        self.db = db_session

    def mint(self, holder_id: str, energy_amount_he: float,
             energy_value_usd: float) -> dict:
        """
        Mint a new certificate with deterministic SHA256 ID.
        certificate_id = HC-{SHA256(key + amount + epoch + rate)[:24]}
        """
        if energy_amount_he < HeliosConfig.CERTIFICATE_MIN_ENERGY_HE:
            raise ValueError(
                f"Minimum {HeliosConfig.CERTIFICATE_MIN_ENERGY_HE} HE required. Got {energy_amount_he}."
            )

        # Verify holder exists
        member = self.db.query(Member).filter_by(helios_id=holder_id).first()
        if not member:
            raise ValueError(f"Key {holder_id} not found")

        mint_rate = energy_amount_he / energy_value_usd if energy_value_usd > 0 else 1.0
        epoch_ts = int(time.time())

        # Deterministic cryptographic ID
        content_hash = Certificate.compute_certificate_hash(
            holder_id, energy_amount_he, epoch_ts, mint_rate
        )
        cert_id = Certificate.generate_certificate_id(content_hash)

        cert = Certificate(
            certificate_id=cert_id,
            content_hash=content_hash,
            holder_id=holder_id,
            energy_amount_he=energy_amount_he,
            energy_value_usd=energy_value_usd,
            mint_rate=mint_rate,
            state=HeliosConfig.CERTIFICATE_STATE_ACTIVE,
            is_final=False
        )

        self.db.add(cert)
        self.db.commit()

        return cert.to_dict()

    # === RRR Covenant Check =============================================

    def check_rrr_covenant(self) -> dict:
        """
        Check the Reserve Ratio covenant before any redemption.
        Returns status and whether redemption is permitted.
        RRR < 1.0 = BLOCKED (auto-pause). No human override.
        """
        from core.metrics import MetricsEngine
        metrics = MetricsEngine(self.db)
        rrr = metrics.get_reserve_ratio()

        return {
            "ratio": rrr["rrr"],
            "status": rrr["status"],
            "redemption_permitted": rrr["status"] != "critical",
            "warning": rrr["status"] == "warning",
            "message": self._rrr_message(rrr["status"])
        }

    def _rrr_message(self, status: str) -> str:
        if status == "critical":
            return ("Redemptions auto-paused. Reserve ratio below 1.0. "
                    "This is an enforced covenant, not a discretionary hold.")
        elif status == "warning":
            return ("Reserve ratio below 3.0. Redemption will proceed, "
                    "but protocol reserves are under pressure.")
        return "Reserve ratio healthy. Redemption proceeds normally."

    # === Redemption (RRR-gated) =========================================

    def redeem_gold(self, certificate_id: str, mvr_id: str = None) -> dict:
        """
        Redeem certificate for gold. Gated by RRR covenant.
        State: ACTIVE -> REDEEMED
        """
        # RRR covenant check
        covenant = self.check_rrr_covenant()
        if not covenant["redemption_permitted"]:
            raise ValueError(covenant["message"])

        cert = self._get_active_certificate(certificate_id)

        cert.state = HeliosConfig.CERTIFICATE_STATE_REDEEMED
        cert.redemption_type = "GOLD"
        cert.redemption_amount = cert.energy_value_usd
        cert.linked_mvr_id = mvr_id
        cert.redeemed_at = datetime.now(timezone.utc)
        cert.is_final = True

        self.db.commit()

        result = {
            "certificate_id": certificate_id,
            "content_hash": cert.content_hash,
            "action": "redeemed_gold",
            "energy_returned_he": cert.energy_amount_he,
            "value_usd": cert.energy_value_usd,
            "linked_mvr": mvr_id,
            "redeemed_at": cert.redeemed_at.isoformat(),
            "is_final": True
        }
        if covenant["warning"]:
            result["rrr_warning"] = covenant["message"]
        return result

    def redeem_stablecoin(self, certificate_id: str) -> dict:
        """
        Redeem certificate for stablecoin. Gated by RRR covenant.
        State: ACTIVE -> REDEEMED
        """
        # RRR covenant check
        covenant = self.check_rrr_covenant()
        if not covenant["redemption_permitted"]:
            raise ValueError(covenant["message"])

        cert = self._get_active_certificate(certificate_id)

        cert.state = HeliosConfig.CERTIFICATE_STATE_REDEEMED
        cert.redemption_type = "STABLECOIN"
        cert.redemption_amount = cert.energy_value_usd
        cert.redeemed_at = datetime.now(timezone.utc)
        cert.is_final = True

        self.db.commit()

        result = {
            "certificate_id": certificate_id,
            "content_hash": cert.content_hash,
            "action": "redeemed_stablecoin",
            "energy_returned_he": cert.energy_amount_he,
            "value_usd": cert.energy_value_usd,
            "redeemed_at": cert.redeemed_at.isoformat(),
            "is_final": True
        }
        if covenant["warning"]:
            result["rrr_warning"] = covenant["message"]
        return result

    # === Cancellation (irreversible) ====================================

    def cancel(self, certificate_id: str) -> dict:
        """
        Cancel certificate. 2% energy is BURNED permanently.
        This is the only action in HELIOS that permanently reduces circulating energy.
        State: ACTIVE -> CANCELLED (irreversible, no reactivation path)
        """
        cert = self._get_active_certificate(certificate_id)

        friction = cert.energy_value_usd * HeliosConfig.CERTIFICATE_CANCEL_FRICTION
        burned_he = cert.energy_amount_he * HeliosConfig.CERTIFICATE_CANCEL_FRICTION
        returned = cert.energy_value_usd - friction

        cert.state = HeliosConfig.CERTIFICATE_STATE_CANCELLED
        cert.redemption_type = "CANCEL"
        cert.redemption_amount = returned
        cert.friction_paid = friction
        cert.energy_burned_he = burned_he
        cert.redeemed_at = datetime.now(timezone.utc)
        cert.is_final = True  # Irreversible. No reactivation path exists.

        self.db.commit()

        return {
            "certificate_id": certificate_id,
            "content_hash": cert.content_hash,
            "action": "cancelled",
            "original_value_usd": cert.energy_value_usd,
            "friction_2_percent": round(friction, 2),
            "energy_burned_he": round(burned_he, 4),
            "returned_usd": round(returned, 2),
            "cancelled_at": cert.redeemed_at.isoformat(),
            "is_final": True,
            "irreversible": True,
            "note": "2% energy permanently burned. This action cannot be undone."
        }

    # === Queries ========================================================

    def get_certificate(self, certificate_id: str) -> dict:
        """Get a certificate by ID or content hash."""
        cert = self.db.query(Certificate).filter_by(certificate_id=certificate_id).first()
        if not cert:
            # Try by content hash
            cert = self.db.query(Certificate).filter_by(content_hash=certificate_id).first()
        if not cert:
            raise ValueError(f"Certificate {certificate_id} not found")
        return cert.to_dict()

    def list_certificates(self, holder_id: str = None,
                           state: str = None, limit: int = 50,
                           offset: int = 0) -> list:
        """List certificates with optional filters."""
        query = self.db.query(Certificate)
        if holder_id:
            query = query.filter_by(holder_id=holder_id)
        if state:
            query = query.filter_by(state=state)
        return [c.to_dict() for c in query.order_by(Certificate.created_at.desc()).offset(offset).limit(limit).all()]

    def get_portfolio(self, holder_id: str) -> dict:
        """Get full certificate portfolio for a key."""
        certs = self.db.query(Certificate).filter_by(holder_id=holder_id).all()

        active = [c for c in certs if c.state == "active"]
        redeemed = [c for c in certs if c.state == "redeemed"]
        cancelled = [c for c in certs if c.state == "cancelled"]

        return {
            "holder_id": holder_id,
            "total_certificates": len(certs),
            "active": {
                "count": len(active),
                "total_he": sum(c.energy_amount_he for c in active),
                "total_usd": sum(c.energy_value_usd for c in active)
            },
            "redeemed": {
                "count": len(redeemed),
                "total_he": sum(c.energy_amount_he for c in redeemed),
                "total_usd": sum(c.redemption_amount or 0 for c in redeemed)
            },
            "cancelled": {
                "count": len(cancelled),
                "total_friction": sum(c.friction_paid or 0 for c in cancelled),
                "total_energy_burned_he": sum(c.energy_burned_he or 0 for c in cancelled)
            }
        }

    def get_total_burned(self) -> dict:
        """Total energy permanently burned across all cancellations."""
        cancelled = self.db.query(Certificate).filter_by(state="cancelled").all()
        total_burned_he = sum(c.energy_burned_he or 0 for c in cancelled)
        total_burned_usd = sum(c.friction_paid or 0 for c in cancelled)
        return {
            "total_certificates_cancelled": len(cancelled),
            "total_energy_burned_he": round(total_burned_he, 4),
            "total_energy_burned_usd": round(total_burned_usd, 2),
            "note": "This energy is permanently destroyed. It can never re-enter the system."
        }

    # === Internal =======================================================

    def _get_active_certificate(self, certificate_id: str) -> Certificate:
        """Get an active certificate or raise."""
        cert = self.db.query(Certificate).filter_by(certificate_id=certificate_id).first()
        if not cert:
            raise ValueError(f"Certificate {certificate_id} not found")
        if cert.is_final:
            raise ValueError(
                f"Certificate {certificate_id} is final ({cert.state}). "
                "No further actions permitted. This is irreversible."
            )
        if cert.state != HeliosConfig.CERTIFICATE_STATE_ACTIVE:
            raise ValueError(f"Certificate {certificate_id} is {cert.state}, not active")
        return cert
