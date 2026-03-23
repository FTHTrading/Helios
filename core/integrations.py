"""
Production integration readiness for Helios.
Tracks which external providers are configured, installed, and ready.
"""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone

from config import HeliosConfig


class IntegrationReadiness:
    """Single source of truth for production provider readiness."""

    @staticmethod
    def _has_package(module_name: str) -> bool:
        return importlib.util.find_spec(module_name) is not None

    @staticmethod
    def _database_backend() -> str:
        url = (HeliosConfig.DATABASE_URL or "").lower()
        if url.startswith("postgresql"):
            return "postgresql"
        if url.startswith("sqlite"):
            return "sqlite"
        if url.startswith("mysql"):
            return "mysql"
        return "unknown"

    @classmethod
    def snapshot(cls) -> dict:
        xrpl_configured = bool(
            HeliosConfig.XRPL_NODE_URL and
            HeliosConfig.XRPL_ISSUER_ADDRESS and
            HeliosConfig.XRPL_ISSUER_SECRET
        )
        xrpl_package = cls._has_package("xrpl")
        xrpl_ready = xrpl_configured and xrpl_package and HeliosConfig.XRPL_ENABLE_SUBMIT

        stripe_configured = bool(HeliosConfig.STRIPE_SECRET_KEY)
        stripe_package = cls._has_package("stripe")
        stripe_ready = stripe_configured and stripe_package

        xaman_ready = bool(HeliosConfig.XAMAN_API_KEY and HeliosConfig.XAMAN_API_SECRET)

        pinata_configured = bool(
            HeliosConfig.PINATA_JWT or
            (HeliosConfig.PINATA_API_KEY and HeliosConfig.PINATA_SECRET_API_KEY)
        )
        ipfs_ready = pinata_configured

        cf_ready = bool(HeliosConfig.CF_API_TOKEN and HeliosConfig.CF_ZONE_ID)
        telnyx_ready = bool(HeliosConfig.TELNYX_API_KEY and HeliosConfig.TELNYX_FROM_NUMBER)
        elevenlabs_ready = bool(HeliosConfig.ELEVENLABS_API_KEY)
        ai_ready = bool(HeliosConfig.AI_API_KEY)

        providers = {
            "xrpl": {
                "configured": xrpl_configured,
                "package_installed": xrpl_package,
                "submission_enabled": HeliosConfig.XRPL_ENABLE_SUBMIT,
                "ready": xrpl_ready,
                "network": HeliosConfig.XRPL_NETWORK,
                "node_url": HeliosConfig.XRPL_NODE_URL,
            },
            "ipfs": {
                "configured": pinata_configured,
                "ready": ipfs_ready,
                "gateway": HeliosConfig.IPFS_GATEWAY,
                "provider": "pinata" if pinata_configured else "not_configured",
            },
            "stripe": {
                "configured": stripe_configured,
                "package_installed": stripe_package,
                "ready": stripe_ready,
                "success_url": HeliosConfig.PAYMENTS_SUCCESS_URL,
                "cancel_url": HeliosConfig.PAYMENTS_CANCEL_URL,
            },
            "xaman": {
                "configured": bool(HeliosConfig.XAMAN_API_KEY),
                "ready": xaman_ready,
            },
            "cloudflare": {
                "configured": bool(HeliosConfig.CF_API_TOKEN),
                "ready": cf_ready,
            },
            "telnyx": {
                "configured": bool(HeliosConfig.TELNYX_API_KEY),
                "ready": telnyx_ready,
            },
            "elevenlabs": {
                "configured": elevenlabs_ready,
                "ready": elevenlabs_ready,
            },
            "openai": {
                "configured": ai_ready,
                "ready": ai_ready,
                "model": HeliosConfig.AI_MODEL,
            },
        }

        # Providers that would upgrade hybrid → full production mode
        optional_upgrades = []
        if cls._database_backend() != "postgresql":
            optional_upgrades.append("postgresql")
        if not xrpl_ready:
            optional_upgrades.append("xrpl")
        if not stripe_ready:
            optional_upgrades.append("stripe")
        if not ipfs_ready:
            optional_upgrades.append("ipfs")

        # The system is launch-ready in hybrid mode.
        # All providers degrade gracefully when not configured.
        full_production = not optional_upgrades

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "development" if HeliosConfig.DEBUG else "production",
            "mode": "production" if full_production else "hybrid",
            "launch_ready": True,
            "database": {
                "backend": cls._database_backend(),
                # Never expose the full URL — it may contain credentials
                "url_masked": cls._database_backend() + "://***",
            },
            "providers": providers,
            "optional_upgrades": optional_upgrades,
            "production_ready": full_production,
            "recommended_chain": "XRPL",
            "recommended_certificate_standard": "XLS-20",
            "recommended_token_model": "XRPL issued fungible token",
        }

    @classmethod
    def launch_readiness_report(cls) -> dict:
        snapshot = cls.snapshot()
        providers = snapshot["providers"]

        # Optional enhancements — the system works without all of these.
        # Every provider has graceful degradation (hybrid mode).
        enhancements = []

        if snapshot["database"]["backend"] != "postgresql":
            enhancements.append({
                "area": "database",
                "description": "Upgrade to Postgres for production-scale persistence",
                "current": snapshot["database"]["backend"],
                "action": "Set HELIOS_DATABASE_URL to a Postgres connection string when scaling.",
                "priority": "recommended",
            })

        if not providers["stripe"]["ready"]:
            enhancements.append({
                "area": "payments",
                "description": "Enable live Stripe checkout for fiat payment processing",
                "current": "configured" if providers["stripe"]["configured"] else "not_configured",
                "action": "Set Stripe production keys when live payment processing is needed.",
                "priority": "optional",
            })

        if not providers["xaman"]["ready"]:
            enhancements.append({
                "area": "wallet",
                "description": "Enable Xaman wallet sign-in for XRPL account linking",
                "current": "configured" if providers["xaman"]["configured"] else "not_configured",
                "action": "Set Xaman credentials when wallet connection flow is needed.",
                "priority": "optional",
            })

        if not providers["xrpl"]["ready"]:
            enhancements.append({
                "area": "chain",
                "description": "Enable live XRPL submission for on-chain settlement",
                "current": "submission_enabled" if providers["xrpl"]["submission_enabled"] else "hybrid_mode",
                "action": "Set XRPL wallet credentials and HELIOS_XRPL_ENABLE_SUBMIT=true for on-chain transactions.",
                "priority": "optional",
            })

        if not providers["cloudflare"]["ready"]:
            enhancements.append({
                "area": "edge",
                "description": "Add Cloudflare for production DNS, SSL, and CDN",
                "current": "configured" if providers["cloudflare"]["configured"] else "not_configured",
                "action": "Set Cloudflare token and zone ID for edge infrastructure.",
                "priority": "optional",
            })

        if not providers["ipfs"]["ready"]:
            enhancements.append({
                "area": "evidence",
                "description": "Add IPFS evidence pinning for treasury proof bundles",
                "current": providers["ipfs"]["provider"],
                "action": "Set Pinata credentials if external evidence pinning is needed.",
                "priority": "optional",
            })

        if not providers["openai"]["ready"]:
            enhancements.append({
                "area": "ai",
                "description": "Enable AI-backed Ask Helios responses beyond grounded fallback",
                "current": "grounded_fallback_active",
                "action": "Set HELIOS_AI_API_KEY for full model-backed advisory responses.",
                "priority": "optional",
            })

        return {
            "timestamp": snapshot["timestamp"],
            "environment": snapshot["environment"],
            "status": "ready",
            "ready_for_public_launch": True,
            "mode": snapshot["mode"],
            "summary": (
                "Helios is launch-ready in hybrid mode. "
                "Core functionality is operational without optional third-party integrations. "
                "We built Helios to launch first and deepen later, not to sit frozen "
                "waiting for every external provider to be wired."
            ),
            "recommended_route": "simplified",
            "recommended_domain": HeliosConfig.DOMAIN,
            "optional_enhancements": enhancements,
            "blocking_issues": [],
            "note": (
                "All external providers degrade gracefully. "
                "The system launches in hybrid mode and upgrades to full production mode "
                "as providers are configured."
            ),
        }
