"""
Helios OS — Configuration
═══════════════════════════════════════════════════════════════
Neural field protocol. Fixed rules. Settlement follows physics, not position.
No admin overrides. Every parameter is auditable.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() == "true"


class HeliosConfig:
    """
    Immutable protocol parameters.
    Changing these requires a governance vote + code audit.
    """

    # ——— App ——————————————————————————————————————————————
    SECRET_KEY = os.getenv("HELIOS_SECRET_KEY", os.urandom(32).hex())
    DEBUG = _env_bool("HELIOS_DEBUG")
    HOST = os.getenv("HELIOS_HOST", "0.0.0.0")
    PORT = int(os.getenv("HELIOS_PORT", "5050"))
    DOMAIN = "xxxiii.io"

    # ——— Database —————————————————————————————————————————
    DATABASE_URL = os.getenv(
        "HELIOS_DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'data' / 'helios.db'}"
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ——— Token — FIXED SUPPLY, NO MINTING ——————————————————————————
    TOKEN_NAME = "HELIOS"
    TOKEN_SYMBOL = "HLS"
    TOKEN_TOTAL_SUPPLY = 100_000_000        # 100M — hard cap, forever
    TOKEN_DECIMALS = 8
    TOKEN_FOUNDER_LOCK_YEARS = 3            # Founders can't touch for 3 years
    TOKEN_POOL_LOCK_PERCENT = 40            # 40% locked in reward pool
    TOKEN_CIRCULATION_PERCENT = 35          # 35% for network activity
    TOKEN_DEVELOPMENT_PERCENT = 15          # 15% for development (vested)
    TOKEN_RESERVE_PERCENT = 10              # 10% emergency reserve (locked)

    # ═══ NEURAL FIELD — POWER OF 5 ═══════════════════════════════════
    # Each node may hold a maximum of 5 bonds.
    # There is no "above" or "below". Only connected peers in a bounded field.
    FIELD_MAX_BONDS = 5                     # Maximum degree per node
    FIELD_POWER_OF_25 = 25                  # 5 rays × 5 = network strength target
    FIELD_COOLDOWN_HOURS = 24               # Minimum hours between new bonds
    FIELD_ACTIVITY_WINDOW_DAYS = 30         # Rolling activity measurement window

    # ═══ ENERGY PROPAGATION ══════════════════════════════════════════
    # When a new node joins, energy propagates outward from the join event.
    # Strongest at direct bonds, attenuates naturally.
    # weight(hop) = 1 / (2 ^ hop)
    # Never explodes. Never compounds infinitely.
    PROPAGATION_MAX_HOPS = 15               # Energy horizon — max distance
    PROPAGATION_DECAY_BASE = 2              # Denominator base: 1/(base^hop)
    PROPAGATION_MIN_WEIGHT = 0.00003052     # 1/(2^15) — smallest possible weight

    # ═══ ACKNOWLEDGEMENT — ONE-TIME, ON JOIN ══════════════════════════
    # When someone joins, their initiator receives an acknowledgement payment.
    # This is the ONLY direct reward. Everything else propagates through the field.
    ACKNOWLEDGEMENT_AMOUNT = 10.0           # HLS paid to initiator on join
    ACKNOWLEDGEMENT_TYPE = "acknowledgement"

    # ═══ ABSORPTION — FRACTIONAL REMAINDER ════════════════════════════
    # After hop 15, the fractional remainder is absorbed into protocol pools.
    # This funds long-term network stability, not individuals.
    ABSORPTION_STABILITY_PERCENT = 40       # Long-term protocol stability
    ABSORPTION_LIQUIDITY_PERCENT = 25       # Network liquidity depth
    ABSORPTION_INTELLIGENCE_PERCENT = 20    # Protocol intelligence / AI ops
    ABSORPTION_COMPLIANCE_PERCENT = 15      # Compliance & audit buffers

    # ═══ NODE STATES ════════════════════════════════════════════════
    # INSTANTIATED → ACKNOWLEDGED → CONNECTED → PROPAGATING → STABLE
    NODE_STATE_INSTANTIATED = "instantiated"     # Created, no bonds yet
    NODE_STATE_ACKNOWLEDGED = "acknowledged"     # Initiator paid, node active
    NODE_STATE_CONNECTED = "connected"           # Has ≥1 bond
    NODE_STATE_PROPAGATING = "propagating"       # Has ≥3 bonds, field active
    NODE_STATE_STABLE = "stable"                 # Has 5 bonds, fully saturated

    # ═══ BOND STATES ═══════════════════════════════════════════════
    # DISCOVER → BOUND → ACTIVE → INACTIVE
    BOND_STATE_DISCOVER = "discover"        # Intent to connect
    BOND_STATE_BOUND = "bound"              # Bond created, pending activation
    BOND_STATE_ACTIVE = "active"            # Both nodes active, energy flows
    BOND_STATE_INACTIVE = "inactive"        # Dormant — no energy propagation

    # ═══ SETTLEMENT RULES ═════════════════════════════════════════
    SETTLEMENT_MIN_ACTIVITY_SCORE = 10      # Minimum activity to receive energy
    SETTLEMENT_ANTI_FRAUD_THRESHOLD = 0.85  # Similarity score triggers review

    # ——— Identity —————————————————————————————————————————
    IDENTITY_MIN_LENGTH = 3
    IDENTITY_MAX_LENGTH = 24
    IDENTITY_SUFFIX = ".helios"
    IDENTITY_RESERVED = [
        "admin", "helios", "system", "support", "root",
        "founder", "official", "team", "network", "token",
        "protocol", "field", "energy", "bond"
    ]

    # ——— AI Assistant (Ask Helios — The Voice) ————————————————————
    AI_MODEL = os.getenv("HELIOS_AI_MODEL", "gpt-4")
    AI_API_KEY = os.getenv("HELIOS_AI_API_KEY", "")
    AI_MAX_CONTEXT_TURNS = 10
    AI_TEMPERATURE = 0.2                    # Precise, authoritative, no fluff

    # --- ElevenLabs Voice AI -----------------------------------------
    # Male voice. Calm, grounded, authoritative. Never salesy.
    ELEVENLABS_API_KEY = os.getenv("HELIOS_ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID = os.getenv("HELIOS_ELEVENLABS_VOICE_ID", "29vD33N1CtxCmqQRPOHJ")  # Drew (male, authoritative)
    ELEVENLABS_GUIDE_VOICE_ID = os.getenv("HELIOS_GUIDE_VOICE_ID", "2EiwWnXFnvU5JabPnv8n")  # Clyde (older male, deep, warm, wise)
    ELEVENLABS_MODEL = "eleven_monolingual_v1"
    ELEVENLABS_STABILITY = 0.65             # Calm, grounded delivery
    ELEVENLABS_SIMILARITY = 0.80            # Strong voice consistency

    # --- Telnyx SMS / Phone Verification -----------------------------
    TELNYX_API_KEY = os.getenv("HELIOS_TELNYX_API_KEY", "")
    TELNYX_FROM_NUMBER = os.getenv("HELIOS_TELNYX_FROM_NUMBER", "")
    TELNYX_VERIFY_EXPIRY_MINUTES = 10
    TELNYX_MAX_VERIFY_ATTEMPTS = 3

    # ═══ ENTRY — ATOMIC $100 ═══════════════════════════════════════════
    # One price. One transaction. Mint + payment atomic.
    # If payment fails → mint fails. No partial states.
    ENTRY_FEE_USD = 100                     # Fixed entry — never changes

    # ═══ ENERGY ALLOCATION — WHERE THE $100 GOES ════════════════════
    # Every dollar has a destination. No slush funds.
    ENERGY_PROPAGATION_PERCENT = 45         # Flows through bonds to peers
    ENERGY_LIQUIDITY_PERCENT = 20           # Internal LP for redemption depth
    ENERGY_TREASURY_PERCENT = 15            # Surplus → metal purchases
    ENERGY_INFRASTRUCTURE_PERCENT = 10      # Ops, hosting, compliance
    ENERGY_BUFFER_PERCENT = 10              # Protocol buffer / reserve

    # ═══ TREASURY — PRECIOUS METALS SPINE ═══════════════════════════
    # NetSurplus × m = MetalAllocation (APMEX purchases)
    # m adjusts 0.05–0.12 based on treasury health
    TREASURY_METAL_COEFFICIENT = 0.07       # Default metal allocation ratio
    TREASURY_METAL_COEFFICIENT_MIN = 0.05   # Floor
    TREASURY_METAL_COEFFICIENT_MAX = 0.12   # Ceiling
    TREASURY_DEALERS = ["APMEX"]            # Approved bullion dealers
    TREASURY_POLICY_VERSION = "1.0"
    TREASURY_AUDIT_INTERVAL_DAYS = 90       # Quarterly proof-of-reserves

    # Metal types tracked
    METAL_TYPES = ["GOLD", "SILVER", "PLATINUM", "PALLADIUM"]
    METAL_DEFAULT = "GOLD"

    # MVR custody states
    CUSTODY_IN_TREASURY = "in_treasury"
    CUSTODY_IN_VAULT = "in_vault"
    CUSTODY_IN_TRANSIT = "in_transit"
    CUSTODY_DELIVERED = "delivered"
    CUSTODY_STATES = [
        CUSTODY_IN_TREASURY, CUSTODY_IN_VAULT,
        CUSTODY_IN_TRANSIT, CUSTODY_DELIVERED
    ]

    # ═══ CERTIFICATES — STORED ENERGY BATTERIES ═══════════════════
    # HC-NFTs: store energy, redeem for gold or stablecoin, cancel with friction
    CERTIFICATE_CANCEL_FRICTION = 0.02      # 2% friction on cancel
    CERTIFICATE_MIN_ENERGY_HE = 10          # Minimum HE to mint a certificate
    CERTIFICATE_REDEMPTION_TYPES = ["GOLD", "STABLECOIN"]
    CERTIFICATE_STATE_ACTIVE = "active"
    CERTIFICATE_STATE_REDEEMED = "redeemed"
    CERTIFICATE_STATE_CANCELLED = "cancelled"

    # ═══ ENERGY INSTRUMENTS ════════════════════════════════════════
    # 4 instruments, each with a distinct role
    ENERGY_NAME = "Helios Name"             # Identity NFT (name.helios)
    ENERGY_HE = "Helios Energy"             # HE — utility unit, flows
    ENERGY_HC_NFT = "Helios Certificate"    # HC-NFT — stored energy battery
    ENERGY_HVC = "Helios Vault Credit"      # HVC — internal accounting unit

    # Energy event types (ledger)
    ENERGY_EVENT_IN = "ENERGY_IN"           # Entry payment → energy injected
    ENERGY_EVENT_ROUTE = "ENERGY_ROUTE"     # Propagation through bonds
    ENERGY_EVENT_STORE = "ENERGY_STORE"     # Stored into certificate
    ENERGY_EVENT_POOL = "ENERGY_POOL"       # Absorbed into protocol pool
    ENERGY_EVENT_BURN = "ENERGY_BURN"       # Compliance or protocol burn
    ENERGY_EVENT_REDEEM = "ENERGY_REDEEM"   # Certificate → gold/stablecoin
    ENERGY_EVENT_CANCEL = "ENERGY_CANCEL"   # Certificate cancel (2% friction)
    ENERGY_EVENT_TYPES = [
        ENERGY_EVENT_IN, ENERGY_EVENT_ROUTE, ENERGY_EVENT_STORE,
        ENERGY_EVENT_POOL, ENERGY_EVENT_BURN, ENERGY_EVENT_REDEEM,
        ENERGY_EVENT_CANCEL
    ]

    # ═══ PREMIUM TIERS ═════════════════════════════════════════════
    # Membership is free after entry. Vault access is premium.
    TIER_BASE = "base"                      # Free after $100 entry
    TIER_PLUS = "plus"                      # Vault Access — monthly
    TIER_PRO = "pro"                        # Vault + Spaces + Credentials
    TIER_OPERATOR = "operator"              # Full operator suite
    TIER_PLUS_MONTHLY_USD = 20
    TIER_PRO_MONTHLY_USD = 99
    TIER_OPERATOR_MONTHLY_USD = 499
    TIERS = [TIER_BASE, TIER_PLUS, TIER_PRO, TIER_OPERATOR]

    # ═══ SPACES & ROOMS ═══════════════════════════════════════════
    SPACE_MAX_ROOMS = 10                    # Max rooms per space
    SPACE_EVENT_FEE_MIN_USD = 50            # Minimum event ticket price
    SPACE_EVENT_FEE_MAX_USD = 250           # Maximum event ticket price
    SPACE_PLATFORM_TAKE_PERCENT = 8         # Platform take on space revenue

    # ═══ CREDENTIALS ══════════════════════════════════════════════
    CREDENTIAL_TYPES = ["operator", "vendor", "host", "educator", "auditor"]
    CREDENTIAL_OPERATOR_FEE_USD = 500       # Annual operator credential
    CREDENTIAL_VENDOR_FEE_USD = 250         # Annual vendor credential
    CREDENTIAL_HOST_FEE_USD = 250           # Annual host credential
    CREDENTIAL_VALIDITY_DAYS = 365          # 1-year credential cycle

    # ═══ SR-LEVEL METRICS ═════════════════════════════════════════
    # Reserve Ratio (RRR): LiquidTreasury / 30d_Redeem_Demand
    METRICS_RRR_HEALTHY = 3.0               # Healthy: 3x coverage
    METRICS_RRR_WARNING = 1.5               # Warning threshold
    METRICS_RRR_CRITICAL = 1.0              # Critical — pause redemptions

    # Flow Efficiency: η = (Routed + Stored + Pooled) / In
    METRICS_FLOW_EFFICIENCY_TARGET = 0.95   # Target 95%+ efficiency

    # Churn Pressure: CancelRequests / ActiveNodes
    METRICS_CHURN_HEALTHY = 0.02            # <2% is healthy
    METRICS_CHURN_WARNING = 0.05            # 5% triggers review

    # Energy Velocity: Transfers_7d / StoredEnergy
    METRICS_VELOCITY_TARGET = 0.3           # Healthy circulation rate

    # Fraud Risk
    METRICS_FRAUD_THRESHOLD = 0.85          # Similarity score triggers review

    # ——— Blockchain Bridge — XRPL ——————————————————————————————————
    CHAIN_RPC_URL = os.getenv("HELIOS_CHAIN_RPC", "")
    CHAIN_ID = int(os.getenv("HELIOS_CHAIN_ID", "1"))
    CHAIN_CONTRACT_ADDRESS = os.getenv("HELIOS_CONTRACT", "")

    # XRPL is the recommended production chain for this codebase.
    XRPL_NETWORK = os.getenv("HELIOS_XRPL_NETWORK", "testnet")
    XRPL_NODE_URL = os.getenv(
        "HELIOS_XRPL_NODE",
        "https://s.altnet.rippletest.net:51234" if XRPL_NETWORK == "testnet" else "https://s1.ripple.com:51234"
    )
    XRPL_ENABLE_SUBMIT = _env_bool("HELIOS_XRPL_ENABLE_SUBMIT")
    XRPL_WALLET_ADDRESS = os.getenv("HELIOS_XRPL_WALLET", "")
    XRPL_WALLET_SECRET = os.getenv("HELIOS_XRPL_SECRET", "")
    XRPL_ISSUER_ADDRESS = os.getenv("HELIOS_XRPL_ISSUER_WALLET", XRPL_WALLET_ADDRESS)
    XRPL_ISSUER_SECRET = os.getenv("HELIOS_XRPL_ISSUER_SECRET", XRPL_WALLET_SECRET)
    XRPL_TREASURY_ADDRESS = os.getenv("HELIOS_XRPL_TREASURY_WALLET", XRPL_ISSUER_ADDRESS)
    XRPL_TREASURY_SECRET = os.getenv("HELIOS_XRPL_TREASURY_SECRET", XRPL_ISSUER_SECRET)

    # ——— IPFS — Evidence Bundle Storage ————————————————————————————
    IPFS_GATEWAY = os.getenv("HELIOS_IPFS_GATEWAY", "https://ipfs.io/ipfs/")
    IPFS_API_URL = os.getenv("HELIOS_IPFS_API", "")
    PINATA_JWT = os.getenv("HELIOS_PINATA_JWT", "")
    PINATA_API_KEY = os.getenv("HELIOS_PINATA_API_KEY", "")
    PINATA_SECRET_API_KEY = os.getenv("HELIOS_PINATA_SECRET_API_KEY", "")

    # ——— Payments / Funding ———————————————————————————————————————
    STRIPE_SECRET_KEY = os.getenv("HELIOS_STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("HELIOS_STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("HELIOS_STRIPE_WEBHOOK_SECRET", "")
    PAYMENTS_SUCCESS_URL = os.getenv("HELIOS_PAYMENTS_SUCCESS_URL", f"https://{DOMAIN}/activate")
    PAYMENTS_CANCEL_URL = os.getenv("HELIOS_PAYMENTS_CANCEL_URL", f"https://{DOMAIN}/join")

    # ——— Wallet Provider / Xaman ———————————————————————————————————
    XAMAN_API_KEY = os.getenv("HELIOS_XAMAN_API_KEY", "")
    XAMAN_API_SECRET = os.getenv("HELIOS_XAMAN_API_SECRET", "")

    # ——— Operations / Background Processing —————————————————————————
    REDIS_URL = os.getenv("HELIOS_REDIS_URL", "")
    SENTRY_DSN = os.getenv("HELIOS_SENTRY_DSN", "")
    RATE_LIMIT_STORAGE_URI = REDIS_URL or "memory://"
    RATE_LIMIT_DEFAULT = os.getenv("HELIOS_RATE_LIMIT_DEFAULT", "200 per hour;50 per minute")

    # ——— Cloudflare / DNS — xxxiii.io ——————————————————————————————
    CF_API_TOKEN = os.getenv("HELIOS_CF_TOKEN", "")
    CF_ZONE_ID = os.getenv("HELIOS_CF_ZONE_ID", "")

    @classmethod
    def validate(cls):
        """Verify all allocation splits sum correctly."""
        # Token allocation
        token_total = (
            cls.TOKEN_POOL_LOCK_PERCENT +
            cls.TOKEN_CIRCULATION_PERCENT +
            cls.TOKEN_DEVELOPMENT_PERCENT +
            cls.TOKEN_RESERVE_PERCENT
        )
        assert token_total == 100, f"Token allocation must be 100%, got {token_total}%"

        # Absorption pools
        absorption_total = (
            cls.ABSORPTION_STABILITY_PERCENT +
            cls.ABSORPTION_LIQUIDITY_PERCENT +
            cls.ABSORPTION_INTELLIGENCE_PERCENT +
            cls.ABSORPTION_COMPLIANCE_PERCENT
        )
        assert absorption_total == 100, f"Absorption split must be 100%, got {absorption_total}%"

        # Energy allocation from entry fee
        energy_total = (
            cls.ENERGY_PROPAGATION_PERCENT +
            cls.ENERGY_LIQUIDITY_PERCENT +
            cls.ENERGY_TREASURY_PERCENT +
            cls.ENERGY_INFRASTRUCTURE_PERCENT +
            cls.ENERGY_BUFFER_PERCENT
        )
        assert energy_total == 100, f"Energy allocation must be 100%, got {energy_total}%"

        # Structural invariants
        assert cls.FIELD_MAX_BONDS == 5, "Power of 5: max bonds must be 5"
        assert cls.PROPAGATION_MAX_HOPS == 15, "Propagation horizon must be 15"
        assert cls.ENTRY_FEE_USD == 100, "Entry fee is fixed at $100"
        assert cls.CERTIFICATE_CANCEL_FRICTION == 0.02, "Cancel friction must be 2%"

        # Metal coefficient bounds
        assert cls.TREASURY_METAL_COEFFICIENT_MIN <= cls.TREASURY_METAL_COEFFICIENT <= cls.TREASURY_METAL_COEFFICIENT_MAX, \
            f"Metal coefficient {cls.TREASURY_METAL_COEFFICIENT} outside bounds"

        return True
