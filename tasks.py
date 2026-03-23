"""
Helios OS — Background Tasks
═════════════════════════════
Celery tasks for automatic settlement, IPFS pinning, and health checks.
All tasks are idempotent — safe to retry on failure.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

from celery_app import celery

log = logging.getLogger("helios.tasks")


def _get_db_session():
    """Create a standalone DB session for use outside Flask request context."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import HeliosConfig

    engine = create_engine(HeliosConfig.DATABASE_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()


def _idempotency_key(*parts) -> str:
    """Generate an idempotency key from parts to prevent double-execution."""
    payload = "|".join(str(p) for p in parts)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SETTLEMENT TASKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def run_scheduled_settlement(self):
    """
    Automatic settlement scheduler.
    Finds unsettled energy events and propagates them through the neural field.
    Runs every 30 minutes via Celery Beat.

    Idempotent: skips events that are already marked 'settled'.
    """
    session = _get_db_session()
    try:
        from models.energy_event import EnergyEvent
        from models.reward import Reward
        from core.rewards import PropagationEngine

        # Find unsettled join events
        unsettled = session.query(EnergyEvent).filter(
            EnergyEvent.event_type == "ENERGY_IN",
            EnergyEvent.status == "pending",
        ).order_by(EnergyEvent.created_at.asc()).limit(50).all()

        if not unsettled:
            log.info("Settlement: no pending events.")
            return {"settled": 0, "skipped": 0}

        engine = PropagationEngine(session)
        settled_count = 0
        skipped_count = 0

        for event in unsettled:
            idem_key = _idempotency_key("settlement", event.id, event.created_at)

            # Check if already settled (idempotency)
            existing = session.query(Reward).filter(
                Reward.reason.like(f"%idem:{idem_key}%")
            ).first()
            if existing:
                skipped_count += 1
                continue

            try:
                energy_amount = Decimal(str(event.amount_he))
                result = engine.execute_propagation(
                    origin_id=event.from_id,
                    energy_amount=energy_amount,
                    event_type="join"
                )

                # Mark event as settled
                event.status = "settled"
                event.settled_at = datetime.now(timezone.utc)
                session.commit()
                settled_count += 1

                log.info(
                    "Settlement complete: event=%s origin=%s distributions=%d",
                    event.id, event.from_id, result.get("distribution_count", 0)
                )
            except Exception as exc:
                session.rollback()
                log.error("Settlement failed for event %s: %s", event.id, exc)

        return {"settled": settled_count, "skipped": skipped_count}

    except Exception as exc:
        session.rollback()
        log.error("Settlement scheduler error: %s", exc)
        raise self.retry(exc=exc)
    finally:
        session.close()


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def execute_single_settlement(self, origin_id: str, energy_amount: float,
                                event_type: str = "join",
                                idempotency_key: str = None):
    """
    Execute settlement propagation for a single event.
    Called on-demand (e.g., after a new member joins).
    """
    session = _get_db_session()
    try:
        if idempotency_key:
            from models.reward import Reward
            existing = session.query(Reward).filter(
                Reward.reason.like(f"%idem:{idempotency_key}%")
            ).first()
            if existing:
                log.info("Settlement already executed for key %s", idempotency_key)
                return {"status": "skipped", "reason": "already_settled"}

        from core.rewards import PropagationEngine
        engine = PropagationEngine(session)
        result = engine.execute_propagation(
            origin_id=origin_id,
            energy_amount=Decimal(str(energy_amount)),
            event_type=event_type,
        )
        return result
    except Exception as exc:
        session.rollback()
        log.error("Single settlement failed: %s", exc)
        raise self.retry(exc=exc)
    finally:
        session.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IPFS / PINATA TASKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@celery.task(bind=True, max_retries=3, default_retry_delay=15)
def pin_nft_metadata(self, metadata: dict, name: str,
                     certificate_id: int = None):
    """
    Pin NFT metadata JSON to IPFS via Pinata.
    If Pinata is not configured, logs a warning and returns simulation result.
    Optionally updates the certificate record with the real CID.
    """
    from core.ipfs import IpfsBundleService

    ipfs = IpfsBundleService()
    result = ipfs.pin_json(metadata, name)

    if result.get("stored") and certificate_id:
        session = _get_db_session()
        try:
            from models.certificate import Certificate
            cert = session.query(Certificate).get(certificate_id)
            if cert:
                cert.ipfs_cid = result["cid"]
                cert.metadata_pinned = True
                session.commit()
                log.info("IPFS CID saved for certificate %d: %s", certificate_id, result["cid"])
        except Exception:
            session.rollback()
        finally:
            session.close()

    if not result.get("stored"):
        log.warning("IPFS pin failed for %s: %s", name, result.get("error", "not configured"))

    return result


@celery.task(bind=True, max_retries=2, default_retry_delay=10)
def pin_treasury_evidence(self, mvr_id: str, evidence_bundle: dict):
    """
    Pin treasury/MVR evidence bundle to IPFS and anchor on XRPL.
    """
    from core.ipfs import IpfsBundleService
    from core.xrpl_bridge import XRPLBridge

    ipfs = IpfsBundleService()
    sha256 = ipfs.hash_bundle(evidence_bundle)
    pin_result = ipfs.pin_json(evidence_bundle, f"mvr-{mvr_id}")

    cid = pin_result.get("cid")

    # Anchor to XRPL
    bridge = XRPLBridge()
    anchor_result = bridge.anchor_receipt(mvr_id, sha256, cid)

    return {
        "mvr_id": mvr_id,
        "sha256": sha256,
        "ipfs": pin_result,
        "xrpl_anchor": anchor_result,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH / OPS TASKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@celery.task
def check_integration_health():
    """Periodic health check of all external integrations."""
    from core.integrations import IntegrationReadiness

    snapshot = IntegrationReadiness.snapshot()
    providers = snapshot.get("providers", {})

    unhealthy = [
        name for name, info in providers.items()
        if not info.get("ready")
    ]

    if unhealthy:
        log.warning("Unhealthy integrations: %s", ", ".join(unhealthy))

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_providers": len(providers),
        "healthy": len(providers) - len(unhealthy),
        "unhealthy": unhealthy,
    }
