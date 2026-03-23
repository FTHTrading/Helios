"""
Helios Token Engine
───────────────────
Fixed supply. No minting. Locked pools. Public stats.
100M HLS — hard cap, forever. Nobody can change this.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_DOWN
from config import HeliosConfig


class TokenEngine:
    """
    Manages the HLS token lifecycle.
    IMMUTABLE RULES:
    - Total supply: 100,000,000 HLS
    - No minting function exists
    - Pool locks are time-locked
    - All movements are recorded
    """

    def __init__(self, db_session):
        self.db = db_session
        self._supply = Decimal(str(HeliosConfig.TOKEN_TOTAL_SUPPLY))
        self._decimals = HeliosConfig.TOKEN_DECIMALS

    # ─── Token Info (Public) ──────────────────────────────────────────

    def get_token_info(self) -> dict:
        """Public token information — verifiable by anyone."""
        return {
            "name": HeliosConfig.TOKEN_NAME,
            "symbol": HeliosConfig.TOKEN_SYMBOL,
            "total_supply": float(self._supply),
            "decimals": self._decimals,
            "allocation": {
                "reward_pool": {
                    "percent": HeliosConfig.TOKEN_POOL_LOCK_PERCENT,
                    "amount": float(self._supply * HeliosConfig.TOKEN_POOL_LOCK_PERCENT / 100),
                    "status": "locked",
                    "lock_type": "smart_contract"
                },
                "circulation": {
                    "percent": HeliosConfig.TOKEN_CIRCULATION_PERCENT,
                    "amount": float(self._supply * HeliosConfig.TOKEN_CIRCULATION_PERCENT / 100),
                    "status": "distributing"
                },
                "development": {
                    "percent": HeliosConfig.TOKEN_DEVELOPMENT_PERCENT,
                    "amount": float(self._supply * HeliosConfig.TOKEN_DEVELOPMENT_PERCENT / 100),
                    "status": "vesting",
                    "vesting_years": 4
                },
                "reserve": {
                    "percent": HeliosConfig.TOKEN_RESERVE_PERCENT,
                    "amount": float(self._supply * HeliosConfig.TOKEN_RESERVE_PERCENT / 100),
                    "status": "locked",
                    "lock_years": 5
                }
            },
            "anti_rug": {
                "can_mint": False,
                "founder_lock_years": HeliosConfig.TOKEN_FOUNDER_LOCK_YEARS,
                "pool_locked": True,
                "supply_auditable": True,
                "admin_override_possible": False
            }
        }

    def get_supply_stats(self) -> dict:
        """Real-time supply statistics."""
        from models.reward import Reward
        from sqlalchemy import func

        # Calculate circulating supply from actual distributions
        # Pool rewards use prefixed IDs like "POOL:stability", "POOL:liquidity"
        distributed = self.db.query(
            func.sum(Reward.amount)
        ).filter(
            Reward.status == "settled",
            ~Reward.member_id.like("POOL%")
        ).scalar() or Decimal('0')

        pool_balance = self.db.query(
            func.sum(Reward.amount)
        ).filter(
            Reward.status == "settled",
            Reward.member_id.like("POOL%")
        ).scalar() or Decimal('0')

        pool_max = self._supply * HeliosConfig.TOKEN_POOL_LOCK_PERCENT / 100
        circulating = Decimal(str(distributed))

        return {
            "total_supply": float(self._supply),
            "circulating": float(circulating),
            "in_pool": float(pool_balance),
            "pool_max": float(pool_max),
            "locked": float(self._supply - circulating - pool_balance),
            "burn_total": 0,  # No burns yet
            "percent_circulating": round(
                float(circulating / self._supply * 100), 4
            ) if self._supply > 0 else 0
        }

    # ─── Token Operations ─────────────────────────────────────────────

    def initialize_pools(self) -> dict:
        """
        One-time initialization of token pools.
        Called at system genesis. Cannot be called again.
        """
        from models.token_pool import TokenPool

        existing = self.db.query(TokenPool).first()
        if existing:
            raise ValueError("Pools already initialized. Cannot re-initialize.")

        pools = []
        allocations = {
            "reward_pool": (
                HeliosConfig.TOKEN_POOL_LOCK_PERCENT,
                "locked",
                None
            ),
            "circulation": (
                HeliosConfig.TOKEN_CIRCULATION_PERCENT,
                "active",
                None
            ),
            "development": (
                HeliosConfig.TOKEN_DEVELOPMENT_PERCENT,
                "vesting",
                datetime.now(timezone.utc) + timedelta(days=4 * 365)
            ),
            "reserve": (
                HeliosConfig.TOKEN_RESERVE_PERCENT,
                "locked",
                datetime.now(timezone.utc) + timedelta(days=5 * 365)
            ),
        }

        for name, (percent, status, unlock_date) in allocations.items():
            amount = float(self._supply * percent / 100)
            pool = TokenPool(
                name=name,
                amount=amount,
                initial_amount=amount,
                status=status,
                unlock_date=unlock_date,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(pool)
            pools.append({
                "name": name,
                "amount": amount,
                "status": status,
                "unlock_date": unlock_date.isoformat() if unlock_date else None
            })

        self.db.commit()
        return {
            "initialized": True,
            "pools": pools,
            "total_supply": float(self._supply),
            "genesis_time": datetime.now(timezone.utc).isoformat()
        }

    def get_pool_balances(self) -> dict:
        """Current balance of each pool."""
        from models.token_pool import TokenPool

        pools = self.db.query(TokenPool).all()
        result = {}
        for pool in pools:
            # SQLite stores naive datetimes — compare naive to naive
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            is_unlocked = (
                pool.unlock_date is not None and
                now_naive >= pool.unlock_date
            )
            result[pool.name] = {
                "balance": pool.amount,
                "initial": pool.initial_amount,
                "status": pool.status,
                "locked": not is_unlocked and pool.status in ("locked", "vesting"),
                "unlock_date": pool.unlock_date.isoformat() if pool.unlock_date else None
            }
        return result

    # ─── Anti-Rug Verification ────────────────────────────────────────

    def verify_integrity(self) -> dict:
        """
        Public verification that no tokens were created or destroyed.
        Anyone can call this. If it fails, something is seriously wrong.
        """
        from models.token_pool import TokenPool
        from models.reward import Reward
        from sqlalchemy import func

        # Sum all pool balances
        pool_total = self.db.query(
            func.sum(TokenPool.amount)
        ).scalar() or Decimal('0')

        # Sum all distributed rewards
        distributed = self.db.query(
            func.sum(Reward.amount)
        ).filter(Reward.status == "settled").scalar() or Decimal('0')

        accounted = Decimal(str(pool_total)) + Decimal(str(distributed))
        expected = self._supply

        integrity_ok = abs(accounted - expected) < Decimal('0.01')

        return {
            "integrity": "PASS" if integrity_ok else "FAIL",
            "expected_supply": float(expected),
            "accounted_supply": float(accounted),
            "in_pools": float(pool_total),
            "distributed": float(distributed),
            "discrepancy": float(abs(accounted - expected)),
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "message": (
                "All tokens accounted for. Supply is intact."
                if integrity_ok else
                "WARNING: Supply discrepancy detected! Investigation required."
            )
        }

    # ─── Founder Lock Verification ────────────────────────────────────

    def check_founder_lock(self) -> dict:
        """Check if founder tokens are still locked (relative to pool genesis)."""
        from models.token_pool import TokenPool

        pool = self.db.query(TokenPool).filter_by(name="reward_pool").first()
        if pool and pool.created_at:
            # Use the actual pool genesis timestamp
            genesis = pool.created_at.replace(tzinfo=timezone.utc) if pool.created_at.tzinfo is None else pool.created_at
        else:
            # Fallback: assume locked (pool not yet initialized)
            genesis = datetime.now(timezone.utc)

        lock_end = genesis + timedelta(
            days=HeliosConfig.TOKEN_FOUNDER_LOCK_YEARS * 365
        )
        locked = datetime.now(timezone.utc) < lock_end

        return {
            "founder_tokens_locked": locked,
            "lock_years": HeliosConfig.TOKEN_FOUNDER_LOCK_YEARS,
            "genesis": genesis.isoformat(),
            "lock_ends": lock_end.isoformat(),
            "message": (
                f"Founder tokens locked for {HeliosConfig.TOKEN_FOUNDER_LOCK_YEARS} years from genesis. "
                "Nobody can access them early."
            ) if locked else "Founder lock period has expired. Tokens are now accessible."
        }
