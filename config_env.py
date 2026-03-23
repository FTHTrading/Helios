"""
Helios OS — Environment Validation & Production Config Separation
═══════════════════════════════════════════════════════════════════
Fail-fast on boot if critical secrets or services are missing.
Separate dev / staging / production requirements.
"""

import os
import sys
import logging

log = logging.getLogger("helios.config")

# ─── Environment Detection ────────────────────────────────────────────

HELIOS_ENV = os.getenv("HELIOS_ENV", "development").lower()
IS_PRODUCTION = HELIOS_ENV == "production"
IS_STAGING = HELIOS_ENV == "staging"
IS_DEVELOPMENT = HELIOS_ENV == "development"
IS_TESTING = HELIOS_ENV == "testing"

# ─── Validation Rules ─────────────────────────────────────────────────

# Keys that MUST be set (non-empty) in production
REQUIRED_PRODUCTION = [
    "HELIOS_SECRET_KEY",
    "HELIOS_API_KEY",
    "HELIOS_DATABASE_URL",
    "HELIOS_REDIS_URL",
]

# Keys that SHOULD be set in production (warning, not fatal)
RECOMMENDED_PRODUCTION = [
    "HELIOS_SENTRY_DSN",
    "HELIOS_STRIPE_SECRET_KEY",
    "HELIOS_STRIPE_PUBLISHABLE_KEY",
    "HELIOS_XRPL_ISSUER_WALLET",
    "HELIOS_XRPL_ISSUER_SECRET",
    "HELIOS_XRPL_TREASURY_WALLET",
    "HELIOS_XRPL_TREASURY_SECRET",
    "HELIOS_XAMAN_API_KEY",
    "HELIOS_XAMAN_API_SECRET",
    "HELIOS_PINATA_JWT",
    "HELIOS_TELNYX_API_KEY",
    "HELIOS_TELNYX_FROM_NUMBER",
]

# Dangerous defaults that must not appear in production
DANGEROUS_DEFAULTS = {
    "HELIOS_SECRET_KEY": [
        "helios-dev-key-change-me-in-production",
        "change-me-before-production",
        "change-me-in-production",
        "secret",
        "dev",
    ],
}


def validate_environment() -> dict:
    """
    Validate the environment for the current HELIOS_ENV.
    Returns a dict with 'valid', 'errors', 'warnings'.
    In production mode, raises SystemExit on critical errors.
    """
    errors = []
    warnings = []

    # 1. Check DEBUG is off in production
    debug_val = os.getenv("HELIOS_DEBUG", "false").lower()
    if IS_PRODUCTION and debug_val == "true":
        errors.append("HELIOS_DEBUG=true is not allowed in production. Set HELIOS_DEBUG=false.")

    # 2. Check required keys
    if IS_PRODUCTION or IS_STAGING:
        for key in REQUIRED_PRODUCTION:
            val = os.getenv(key, "").strip()
            if not val:
                errors.append(f"{key} is required in {HELIOS_ENV} but is empty or unset.")

    # 3. Check dangerous defaults
    for key, bad_values in DANGEROUS_DEFAULTS.items():
        val = os.getenv(key, "").strip().lower()
        if val in [v.lower() for v in bad_values]:
            if IS_PRODUCTION:
                errors.append(f"{key} is set to a dangerous default value. Generate a real secret.")
            else:
                warnings.append(f"{key} is using a dev default — change before production.")

    # 4. Check recommended keys
    if IS_PRODUCTION:
        for key in RECOMMENDED_PRODUCTION:
            val = os.getenv(key, "").strip()
            if not val:
                warnings.append(f"{key} is not set. Some features will be unavailable.")

    # 5. Database check — production must not use SQLite
    db_url = os.getenv("HELIOS_DATABASE_URL", "").lower()
    if IS_PRODUCTION and ("sqlite" in db_url or not db_url):
        errors.append("SQLite is not suitable for production. Set HELIOS_DATABASE_URL to a PostgreSQL URI.")

    # 6. XRPL network check
    xrpl_network = os.getenv("HELIOS_XRPL_NETWORK", "testnet").lower()
    if IS_PRODUCTION and xrpl_network == "testnet":
        warnings.append("XRPL is on testnet. Set HELIOS_XRPL_NETWORK=mainnet for production.")

    result = {
        "valid": len(errors) == 0,
        "environment": HELIOS_ENV,
        "errors": errors,
        "warnings": warnings,
    }

    # Log output
    for w in warnings:
        log.warning("ENV WARNING: %s", w)
    for e in errors:
        log.error("ENV ERROR: %s", e)

    # Fail-fast in production
    if errors and IS_PRODUCTION:
        print("\n" + "=" * 60, file=sys.stderr)
        print("  HELIOS — FATAL: Environment validation failed", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        for w in warnings:
            print(f"  ⚠ {w}", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        sys.exit(1)

    return result
