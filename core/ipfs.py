"""
IPFS / Pinata helpers for Helios evidence bundles.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import HeliosConfig


class IpfsBundleService:
    """Manage evidence bundle hashing and optional Pinata uploads."""

    PINATA_JSON_ENDPOINT = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    def is_ready(self) -> bool:
        return bool(
            HeliosConfig.PINATA_JWT or
            (HeliosConfig.PINATA_API_KEY and HeliosConfig.PINATA_SECRET_API_KEY)
        )

    def hash_bundle(self, bundle: dict) -> str:
        encoded = json.dumps(bundle, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def build_receipt_manifest(self, **kwargs) -> dict:
        manifest = {k: v for k, v in kwargs.items() if v is not None}
        manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
        manifest["protocol"] = "HELIOS"
        return manifest

    def pin_json(self, bundle: dict, name: str) -> dict:
        digest = self.hash_bundle(bundle)
        if not self.is_ready():
            return {
                "stored": False,
                "simulation": True,
                "cid": None,
                "sha256": digest,
                "message": "Pinata credentials not configured.",
            }

        payload = json.dumps({
            "pinataContent": bundle,
            "pinataMetadata": {"name": name},
        }).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
        }
        if HeliosConfig.PINATA_JWT:
            headers["Authorization"] = f"Bearer {HeliosConfig.PINATA_JWT}"
        else:
            headers["pinata_api_key"] = HeliosConfig.PINATA_API_KEY
            headers["pinata_secret_api_key"] = HeliosConfig.PINATA_SECRET_API_KEY

        request = Request(self.PINATA_JSON_ENDPOINT, data=payload, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
            return {
                "stored": True,
                "simulation": False,
                "cid": data.get("IpfsHash"),
                "sha256": digest,
                "size": data.get("PinSize"),
                "timestamp": data.get("Timestamp"),
            }
        except (HTTPError, URLError, TimeoutError) as exc:
            return {
                "stored": False,
                "simulation": True,
                "cid": None,
                "sha256": digest,
                "error": str(exc),
            }
