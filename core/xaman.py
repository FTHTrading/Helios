"""Xaman (XUMM) wallet payload helpers for XRPL signing flows."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import requests

from config import HeliosConfig


class XamanService:
    BASE_URL = "https://xumm.app/api/v1/platform"

    def __init__(self):
        self.api_key = HeliosConfig.XAMAN_API_KEY
        self.api_secret = HeliosConfig.XAMAN_API_SECRET

    def is_ready(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def create_payload(self, action: str, **kwargs) -> dict:
        txjson = self._build_tx(action, **kwargs)
        if not self.is_ready():
            return {
                "created": False,
                "simulation": True,
                "action": action,
                "txjson": txjson,
                "message": "Add HELIOS_XAMAN_API_KEY and HELIOS_XAMAN_API_SECRET to enable wallet signing.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        response = requests.post(
            f"{self.BASE_URL}/payload",
            headers=self._headers(),
            json={"txjson": txjson},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        next_data = data.get("next", {})
        refs = data.get("refs", {})
        return {
            "created": True,
            "simulation": False,
            "action": action,
            "payload_uuid": refs.get("uuid"),
            "qr_png": next_data.get("qr_png"),
            "always": next_data.get("always"),
            "opened": next_data.get("opened"),
            "txjson": txjson,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_payload(self, payload_uuid: str) -> dict:
        if not self.is_ready():
            return {
                "payload_uuid": payload_uuid,
                "resolved": False,
                "signed": False,
                "expired": False,
                "simulation": True,
            }
        response = requests.get(
            f"{self.BASE_URL}/payload/{payload_uuid}",
            headers=self._headers(),
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        meta = data.get("meta", {})
        response_data = data.get("response", {})
        return {
            "payload_uuid": payload_uuid,
            "resolved": meta.get("resolved", False),
            "signed": response_data.get("signed", False),
            "expired": meta.get("expired", False),
            "account": response_data.get("account"),
            "txid": response_data.get("txid"),
            "simulation": False,
        }

    def _build_tx(self, action: str, **kwargs) -> dict:
        if action == "signin":
            return {"TransactionType": "SignIn"}
        if action == "trustline":
            account = kwargs.get("account")
            if not account:
                raise ValueError("account is required for trustline payloads")
            return {
                "TransactionType": "TrustSet",
                "Account": account,
                "LimitAmount": {
                    "currency": HeliosConfig.TOKEN_SYMBOL,
                    "issuer": HeliosConfig.XRPL_ISSUER_ADDRESS,
                    "value": "1000000000",
                },
            }
        if action == "payment":
            account = kwargs.get("account")
            destination = kwargs.get("destination")
            amount = kwargs.get("amount")
            if not all([account, destination, amount]):
                raise ValueError("account, destination, and amount are required for payment payloads")
            return {
                "TransactionType": "Payment",
                "Account": account,
                "Destination": destination,
                "Amount": str(int(float(amount))),
            }
        raise ValueError(f"Unsupported Xaman action: {action}")

    def _headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json",
        }
