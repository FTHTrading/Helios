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

        missing = []
        if cls._database_backend() != "postgresql":
            missing.append("postgresql")
        if not xrpl_ready:
            missing.append("xrpl")
        if not stripe_ready:
            missing.append("stripe")
        if not ipfs_ready:
            missing.append("ipfs")

        production_ready = not missing

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "development" if HeliosConfig.DEBUG else "production",
            "mode": "production" if production_ready else "hybrid",
            "database": {
                "backend": cls._database_backend(),
                "url": HeliosConfig.DATABASE_URL,
            },
            "providers": providers,
            "missing_foundations": missing,
            "production_ready": production_ready,
            "recommended_chain": "XRPL",
            "recommended_certificate_standard": "XLS-20",
            "recommended_token_model": "XRPL issued fungible token",
        }
