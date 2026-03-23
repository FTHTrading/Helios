"""
Metrics Engine — SR-Level Analytics
═══════════════════════════════════════════════════════════════════════
Four key metrics that define protocol health:

RRR (Reserve Ratio):       LiquidTreasury / 30d_Redeem_Demand
η (Flow Efficiency):       (Routed + Stored + Pooled) / In
CP (Churn Pressure):       CancelRequests / ActiveNodes
V (Energy Velocity):       Transfers_7d / StoredEnergy
"""

from datetime import datetime, timezone, timedelta
from config import HeliosConfig
from models.energy_event import EnergyEvent
from models.certificate import Certificate
from models.vault_receipt import VaultReceipt
from models.member import Member


class MetricsEngine:
    """Protocol health metrics. Anyone can verify."""

    def __init__(self, db_session):
        self.db = db_session

    def get_all_metrics(self) -> dict:
        """Get all SR-level metrics in one call."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rrr": self.get_reserve_ratio(),
            "flow_efficiency": self.get_flow_efficiency(),
            "churn_pressure": self.get_churn_pressure(),
            "energy_velocity": self.get_energy_velocity(),
            "network_health": self.get_network_health(),
            "thresholds": {
                "rrr_healthy": HeliosConfig.METRICS_RRR_HEALTHY,
                "rrr_warning": HeliosConfig.METRICS_RRR_WARNING,
                "rrr_critical": HeliosConfig.METRICS_RRR_CRITICAL,
                "flow_efficiency_target": HeliosConfig.METRICS_FLOW_EFFICIENCY_TARGET,
                "churn_healthy": HeliosConfig.METRICS_CHURN_HEALTHY,
                "churn_warning": HeliosConfig.METRICS_CHURN_WARNING,
                "velocity_target": HeliosConfig.METRICS_VELOCITY_TARGET,
            }
        }

    # ═══ RRR — Reserve Ratio ═════════════════════════════════════

    def get_reserve_ratio(self) -> dict:
        """
        RRR = LiquidTreasury / 30d_Redeem_Demand
        Healthy ≥ 3.0, Warning ≥ 1.5, Critical < 1.0
        """
        # Liquid treasury = total MVR cost that's still in_treasury
        treasury_mvrs = self.db.query(VaultReceipt).filter_by(
            custody_status=HeliosConfig.CUSTODY_IN_TREASURY
        ).all()
        liquid_treasury = sum(m.total_cost_usd for m in treasury_mvrs)

        # 30-day redemption demand
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_redeems = self.db.query(Certificate).filter(
            Certificate.state == "redeemed",
            Certificate.redeemed_at >= thirty_days_ago
        ).all()
        redeem_demand = sum(c.energy_value_usd for c in recent_redeems)

        rrr = liquid_treasury / redeem_demand if redeem_demand > 0 else float('inf')
        if rrr == float('inf'):
            status = "healthy"
        elif rrr >= HeliosConfig.METRICS_RRR_HEALTHY:
            status = "healthy"
        elif rrr >= HeliosConfig.METRICS_RRR_WARNING:
            status = "warning"
        else:
            status = "critical"

        return {
            "metric": "Reserve Ratio (RRR)",
            "formula": "LiquidTreasury / 30d_Redeem_Demand",
            "liquid_treasury_usd": round(liquid_treasury, 2),
            "redeem_demand_30d_usd": round(redeem_demand, 2),
            "rrr": round(rrr, 2) if rrr != float('inf') else "∞",
            "status": status
        }

    # ═══ η — Flow Efficiency ═════════════════════════════════════

    def get_flow_efficiency(self) -> dict:
        """
        η = (Routed + Stored + Pooled) / In
        Target: ≥ 0.95 (95% of injected energy goes where it should)
        """
        from sqlalchemy import func

        # Use SQL GROUP BY instead of loading every event into Python
        rows = self.db.query(
            EnergyEvent.event_type,
            func.sum(EnergyEvent.amount_he).label("total")
        ).group_by(EnergyEvent.event_type).all()

        totals = {row.event_type: float(row.total or 0) for row in rows}

        total_in = totals.get(HeliosConfig.ENERGY_EVENT_IN, 0.0)
        total_routed = totals.get(HeliosConfig.ENERGY_EVENT_ROUTE, 0.0)
        total_stored = totals.get(HeliosConfig.ENERGY_EVENT_STORE, 0.0)
        total_pooled = totals.get(HeliosConfig.ENERGY_EVENT_POOL, 0.0)

        productive = total_routed + total_stored + total_pooled
        eta = productive / total_in if total_in > 0 else 1.0

        status = "healthy" if eta >= HeliosConfig.METRICS_FLOW_EFFICIENCY_TARGET else "below_target"

        return {
            "metric": "Flow Efficiency (η)",
            "formula": "(Routed + Stored + Pooled) / In",
            "total_in": round(total_in, 2),
            "total_productive": round(productive, 2),
            "eta": round(eta, 4),
            "status": status
        }

    # ═══ CP — Churn Pressure ═════════════════════════════════════

    def get_churn_pressure(self) -> dict:
        """
        CP = CancelRequests / ActiveNodes
        Healthy < 0.02, Warning < 0.05
        """
        cancel_count = self.db.query(Certificate).filter_by(
            state="cancelled"
        ).count()

        active_nodes = self.db.query(Member).filter(
            Member.status == "active"
        ).count()

        cp = cancel_count / active_nodes if active_nodes > 0 else 0.0

        if cp < HeliosConfig.METRICS_CHURN_HEALTHY:
            status = "healthy"
        elif cp < HeliosConfig.METRICS_CHURN_WARNING:
            status = "warning"
        else:
            status = "critical"

        return {
            "metric": "Churn Pressure (CP)",
            "formula": "CancelRequests / ActiveNodes",
            "cancel_count": cancel_count,
            "active_nodes": active_nodes,
            "cp": round(cp, 4),
            "status": status
        }

    # ═══ V — Energy Velocity ═════════════════════════════════════

    def get_energy_velocity(self) -> dict:
        """
        V = Transfers_7d / StoredEnergy
        Target: ~0.3 (healthy circulation)
        """
        from sqlalchemy import func
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        transfer_volume = self.db.query(
            func.sum(EnergyEvent.amount_he)
        ).filter(
            EnergyEvent.event_type == HeliosConfig.ENERGY_EVENT_ROUTE,
            EnergyEvent.created_at >= seven_days_ago
        ).scalar() or 0.0
        transfer_volume = float(transfer_volume)

        stored_energy = self.db.query(
            func.sum(Certificate.energy_amount_he)
        ).filter(Certificate.state == "active").scalar() or 0.0
        stored_energy = float(stored_energy)

        velocity = transfer_volume / stored_energy if stored_energy > 0 else 0.0

        return {
            "metric": "Energy Velocity (V)",
            "formula": "Transfers_7d / StoredEnergy",
            "transfers_7d_he": round(transfer_volume, 2),
            "stored_energy_he": round(stored_energy, 2),
            "velocity": round(velocity, 4),
            "target": HeliosConfig.METRICS_VELOCITY_TARGET
        }

    # ═══ Network Health Summary ══════════════════════════════════

    def get_network_health(self) -> dict:
        """Aggregate network health snapshot."""
        total_members = self.db.query(Member).count()
        active_members = self.db.query(Member).filter_by(status="active").count()

        # Node state distribution
        from sqlalchemy import func
        state_dist = self.db.query(
            Member.node_state, func.count(Member.id)
        ).group_by(Member.node_state).all()

        # Certificate health
        active_certs = self.db.query(Certificate).filter_by(state="active").count()
        total_certs = self.db.query(Certificate).count()

        # Energy totals
        from sqlalchemy import func as sa_func
        total_energy_injected = self.db.query(
            sa_func.sum(EnergyEvent.amount_he)
        ).filter(
            EnergyEvent.event_type == HeliosConfig.ENERGY_EVENT_IN
        ).scalar() or 0.0
        total_energy_injected = float(total_energy_injected)

        return {
            "total_nodes": total_members,
            "active_nodes": active_members,
            "node_states": {state: count for state, count in state_dist},
            "certificates": {
                "active": active_certs,
                "total": total_certs
            },
            "total_energy_injected_he": round(total_energy_injected, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
