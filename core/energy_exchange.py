"""
Energy Exchange Engine — Conservation-Law-Enforced Flow System
═══════════════════════════════════════════════════════════════════════
Conservation Law: Total Inflows = Routed + Stored + Pooled + Ops + Buffer

Every $100 entry injects energy. That energy is split per config:
  45% propagation (links), 20% LP, 15% treasury, 10% infra, 10% buffer

The energy ledger records EVERY movement. Nothing is unaccounted for.

4 Instruments:
  - Helios Name (identity)
  - Helios Energy HE (utility unit — flows through links)
  - Helios Certificate HC-NFT (stored energy battery)
  - Helios Vault Credit HVC (internal accounting unit)
"""

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from config import HeliosConfig
from models.energy_event import EnergyEvent
from models.member import Member


class EnergyExchange:
    """The heart of the economic engine. Every unit is tracked."""

    def __init__(self, db_session):
        self.db = db_session

    # ═══ Energy Injection (Entry) ═════════════════════════════════

    def inject_entry_energy(self, member_id: str, amount_usd: float = None) -> dict:
        """
        Inject energy from a $100 entry fee. Atomic split per protocol.
        Returns the complete allocation breakdown.
        """
        amount = amount_usd or HeliosConfig.ENTRY_FEE_USD
        reference_id = f"ENTRY-{uuid.uuid4().hex[:12].upper()}"

        # Verify member exists
        member = self.db.query(Member).filter_by(helios_id=member_id).first()
        if not member:
            raise ValueError(f"Node {member_id} not found")

        # Calculate splits
        propagation = amount * (HeliosConfig.ENERGY_PROPAGATION_PERCENT / 100)
        liquidity = amount * (HeliosConfig.ENERGY_LIQUIDITY_PERCENT / 100)
        treasury = amount * (HeliosConfig.ENERGY_TREASURY_PERCENT / 100)
        infrastructure = amount * (HeliosConfig.ENERGY_INFRASTRUCTURE_PERCENT / 100)
        buffer = amount * (HeliosConfig.ENERGY_BUFFER_PERCENT / 100)

        # Record ENERGY_IN event
        self._record_event(
            event_type=HeliosConfig.ENERGY_EVENT_IN,
            from_id=None,  # External — payment from outside
            to_id=member_id,
            amount_he=amount,
            amount_usd=amount,
            reference_id=reference_id,
            extra_data={"source": "entry_fee"}
        )

        # Record ENERGY_POOL events for non-propagation splits
        pools = {
            "liquidity": liquidity,
            "treasury_surplus": treasury,
            "infrastructure": infrastructure,
            "buffer": buffer
        }
        for pool_name, pool_amount in pools.items():
            self._record_event(
                event_type=HeliosConfig.ENERGY_EVENT_POOL,
                from_id=member_id,
                to_id=f"POOL:{pool_name}",
                amount_he=pool_amount,
                amount_usd=pool_amount,
                pool_name=pool_name,
                reference_id=reference_id
            )

        self.db.commit()

        return {
            "reference_id": reference_id,
            "member_id": member_id,
            "total_injected_usd": amount,
            "allocation": {
                "propagation": round(propagation, 2),
                "liquidity": round(liquidity, 2),
                "treasury_surplus": round(treasury, 2),
                "infrastructure": round(infrastructure, 2),
                "buffer": round(buffer, 2)
            },
            "conservation_check": round(propagation + liquidity + treasury + infrastructure + buffer, 2) == amount
        }

    # ═══ Energy Routing (Propagation) ═════════════════════════════

    def route_energy(self, from_id: str, to_id: str,
                     amount_he: float, hop_number: int,
                     reference_id: str = None) -> dict:
        """
        Route energy through a link. Records the flow in the ledger.
        weight(hop) = 1 / (2 ^ hop)
        """
        self._record_event(
            event_type=HeliosConfig.ENERGY_EVENT_ROUTE,
            from_id=from_id,
            to_id=to_id,
            amount_he=amount_he,
            hop_number=hop_number,
            reference_id=reference_id or f"ROUTE-{uuid.uuid4().hex[:8].upper()}"
        )
        self.db.commit()

        return {
            "event_type": "ENERGY_ROUTE",
            "from_id": from_id,
            "to_id": to_id,
            "amount_he": amount_he,
            "hop_number": hop_number
        }

    # ═══ Energy Storage (Certificate Mint) ════════════════════════

    def store_energy(self, member_id: str, amount_he: float,
                     certificate_id: str) -> dict:
        """Store energy into a certificate (HC-NFT)."""
        if amount_he < HeliosConfig.CERTIFICATE_MIN_ENERGY_HE:
            raise ValueError(
                f"Minimum {HeliosConfig.CERTIFICATE_MIN_ENERGY_HE} HE required to mint certificate"
            )

        self._record_event(
            event_type=HeliosConfig.ENERGY_EVENT_STORE,
            from_id=member_id,
            to_id=f"CERT:{certificate_id}",
            amount_he=amount_he,
            certificate_id=certificate_id,
            reference_id=f"STORE-{uuid.uuid4().hex[:8].upper()}"
        )
        self.db.commit()

        return {
            "event_type": "ENERGY_STORE",
            "member_id": member_id,
            "certificate_id": certificate_id,
            "amount_he": amount_he
        }

    # ═══ Energy Redemption ════════════════════════════════════════

    def redeem_energy(self, certificate_id: str, redemption_type: str,
                      amount_he: float, member_id: str) -> dict:
        """Redeem stored energy from a certificate."""
        if redemption_type not in HeliosConfig.CERTIFICATE_REDEMPTION_TYPES:
            raise ValueError(f"Invalid redemption type: {redemption_type}")

        self._record_event(
            event_type=HeliosConfig.ENERGY_EVENT_REDEEM,
            from_id=f"CERT:{certificate_id}",
            to_id=member_id,
            amount_he=amount_he,
            certificate_id=certificate_id,
            reference_id=f"REDEEM-{uuid.uuid4().hex[:8].upper()}",
            extra_data={"redemption_type": redemption_type}
        )
        self.db.commit()

        return {
            "event_type": "ENERGY_REDEEM",
            "certificate_id": certificate_id,
            "redemption_type": redemption_type,
            "amount_he": amount_he,
            "member_id": member_id
        }

    # ═══ Energy Cancel (with friction) ════════════════════════════

    def cancel_energy(self, certificate_id: str, amount_he: float,
                      member_id: str) -> dict:
        """
        Cancel a certificate. 2% energy is PERMANENTLY BURNED.
        This is the only action in HELIOS that destroys energy.
        The burn is irreversible. The energy can never re-enter the system.
        """
        friction = amount_he * HeliosConfig.CERTIFICATE_CANCEL_FRICTION
        returned = amount_he - friction

        # Record cancel event (energy returned to key)
        self._record_event(
            event_type=HeliosConfig.ENERGY_EVENT_CANCEL,
            from_id=f"CERT:{certificate_id}",
            to_id=member_id,
            amount_he=returned,
            certificate_id=certificate_id,
            reference_id=f"CANCEL-{uuid.uuid4().hex[:8].upper()}",
            extra_data={
                "friction": friction,
                "original_amount": amount_he,
                "irreversible": True
            }
        )

        # Record permanent energy burn (destroyed, not redistributed)
        self._record_event(
            event_type=HeliosConfig.ENERGY_EVENT_BURN,
            from_id=f"CERT:{certificate_id}",
            to_id="BURN:permanent",
            amount_he=friction,
            certificate_id=certificate_id,
            pool_name="permanent_burn",
            reference_id=f"BURN-{uuid.uuid4().hex[:8].upper()}",
            extra_data={
                "burn_type": "certificate_cancellation_friction",
                "irreversible": True,
                "note": "Energy permanently destroyed. Cannot re-enter system."
            }
        )

        self.db.commit()

        return {
            "event_type": "ENERGY_CANCEL",
            "certificate_id": certificate_id,
            "original_amount_he": amount_he,
            "energy_burned_he": round(friction, 4),
            "returned_amount_he": round(returned, 4),
            "member_id": member_id,
            "irreversible": True,
            "note": "2% energy permanently burned. This action cannot be undone."
        }

    # ═══ Conservation Law Verification ════════════════════════════

    def verify_conservation(self) -> dict:
        """
        Conservation Law: total inflows = routed + stored + pooled + ops + buffer
        Verify that the energy ledger balances.
        """
        from sqlalchemy import func

        events = self.db.query(EnergyEvent).all()

        totals = {}
        for e in events:
            et = e.event_type
            totals[et] = totals.get(et, 0.0) + e.amount_he

        total_in = totals.get(HeliosConfig.ENERGY_EVENT_IN, 0.0)
        total_routed = totals.get(HeliosConfig.ENERGY_EVENT_ROUTE, 0.0)
        total_stored = totals.get(HeliosConfig.ENERGY_EVENT_STORE, 0.0)
        total_pooled = totals.get(HeliosConfig.ENERGY_EVENT_POOL, 0.0)
        total_burned = totals.get(HeliosConfig.ENERGY_EVENT_BURN, 0.0)
        total_redeemed = totals.get(HeliosConfig.ENERGY_EVENT_REDEEM, 0.0)
        total_cancelled = totals.get(HeliosConfig.ENERGY_EVENT_CANCEL, 0.0)

        total_out = total_routed + total_stored + total_pooled + total_burned
        # Redeemed and cancelled come from stored energy, not from inflows
        balance = round(total_in - total_out, 4)

        return {
            "conservation_law": "total_in = routed + stored + pooled + burned",
            "total_in": round(total_in, 2),
            "total_routed": round(total_routed, 2),
            "total_stored": round(total_stored, 2),
            "total_pooled": round(total_pooled, 2),
            "total_burned": round(total_burned, 2),
            "total_redeemed": round(total_redeemed, 2),
            "total_cancelled": round(total_cancelled, 2),
            "total_out": round(total_out, 2),
            "balance": balance,
            "balanced": abs(balance) < 0.01,
            "event_count": len(events),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # ═══ Energy Map ═══════════════════════════════════════════════

    def get_energy_map(self, member_id: str = None, limit: int = 100) -> dict:
        """Get energy flow map — all events for a member or the whole field."""
        query = self.db.query(EnergyEvent)

        if member_id:
            query = query.filter(
                (EnergyEvent.from_id == member_id) |
                (EnergyEvent.to_id == member_id)
            )

        events = query.order_by(EnergyEvent.created_at.desc()).limit(limit).all()

        return {
            "member_id": member_id,
            "event_count": len(events),
            "events": [e.to_dict() for e in events]
        }

    def get_energy_balance(self, member_id: str) -> dict:
        """Get total energy balance for a member — inflows minus outflows."""
        events = self.db.query(EnergyEvent).filter(
            (EnergyEvent.from_id == member_id) |
            (EnergyEvent.to_id == member_id)
        ).all()

        inflows = sum(e.amount_he for e in events if e.to_id == member_id)
        outflows = sum(e.amount_he for e in events if e.from_id == member_id)

        return {
            "member_id": member_id,
            "total_inflows_he": round(inflows, 4),
            "total_outflows_he": round(outflows, 4),
            "net_energy_he": round(inflows - outflows, 4),
            "event_count": len(events)
        }

    # ═══ Internal ═════════════════════════════════════════════════

    def _record_event(self, event_type: str, from_id: str, to_id: str,
                      amount_he: float, amount_usd: float = None,
                      hop_number: int = None, certificate_id: str = None,
                      pool_name: str = None, reference_id: str = None,
                      extra_data: dict = None):
        """Record an immutable energy event in the ledger."""
        event = EnergyEvent(
            event_id=f"EV-{uuid.uuid4().hex[:12].upper()}",
            event_type=event_type,
            from_id=from_id,
            to_id=to_id,
            amount_he=amount_he,
            amount_usd=amount_usd,
            hop_number=hop_number,
            certificate_id=certificate_id,
            pool_name=pool_name,
            reference_id=reference_id,
            extra_data=extra_data or {}
        )
        self.db.add(event)
