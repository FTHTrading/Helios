"""Build manifest helpers for launch ownership, watermarking, and route selection."""

from __future__ import annotations

import hashlib

from config import HeliosConfig


def get_build_manifest() -> dict:
    watermark = (HeliosConfig.BUILD_WATERMARK or "").strip()
    launch_key = (HeliosConfig.LAUNCH_KEY or "").strip()
    route = (HeliosConfig.DEPLOYMENT_ROUTE or "full").strip().lower()
    owner = (HeliosConfig.BUILD_OWNER or "FTHTrading").strip()
    build_id = (HeliosConfig.BUILD_ID or "").strip()

    signature_source = "|".join([
        owner,
        route,
        watermark,
        build_id,
        launch_key,
        HeliosConfig.DOMAIN,
    ])
    fingerprint = hashlib.sha256(signature_source.encode("utf-8")).hexdigest()[:12].upper()

    return {
        "owner": owner,
        "route": route,
        "build_id": build_id,
        "watermark": watermark,
        "fingerprint": fingerprint,
        "watermark_enabled": bool(watermark or launch_key or build_id),
    }