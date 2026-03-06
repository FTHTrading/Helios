"""
XRPL bridge for Helios.
Uses real XRPL submission when configured, otherwise falls back to deterministic dry runs.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from datetime import datetime, timezone

from config import HeliosConfig
from core.integrations import IntegrationReadiness


class XRPLBridge:
    """Small adapter over XRPL operations used by Helios."""

    def __init__(self):
        self.node_url = HeliosConfig.XRPL_NODE_URL
        self.network = HeliosConfig.XRPL_NETWORK
        self.issuer_address = HeliosConfig.XRPL_ISSUER_ADDRESS
        self.issuer_secret = HeliosConfig.XRPL_ISSUER_SECRET
        self.treasury_address = HeliosConfig.XRPL_TREASURY_ADDRESS or self.issuer_address
        self.treasury_secret = HeliosConfig.XRPL_TREASURY_SECRET or self.issuer_secret

    def status(self) -> dict:
        return IntegrationReadiness.snapshot()["providers"]["xrpl"]

    def is_ready(self) -> bool:
        return bool(self.status()["ready"])

    def create_member_wallet(self, member_id: str) -> dict:
        """Create an XRPL wallet when the SDK is available, otherwise return a deterministic dry run."""
        if not self.is_ready():
            return self._simulate_wallet(member_id)

        try:
            Wallet = importlib.import_module("xrpl.wallet").Wallet

            wallet = Wallet.create()
            return {
                "chain": "XRPL",
                "classic_address": wallet.classic_address,
                "seed": wallet.seed,
                "simulation": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception:
            return self._simulate_wallet(member_id)

    def submit_trustset(self, account_address: str, account_secret: str,
                        limit_value: str = "1000000000") -> dict:
        payload = {
            "TransactionType": "TrustSet",
            "Account": account_address,
            "LimitAmount": {
                "currency": HeliosConfig.TOKEN_SYMBOL,
                "issuer": self.issuer_address,
                "value": str(limit_value),
            },
        }
        if not self.is_ready() or not account_secret:
            return self._simulate_tx("TrustSet", payload)

        try:
            IssuedCurrencyAmount = importlib.import_module("xrpl.models.amounts").IssuedCurrencyAmount
            TrustSet = importlib.import_module("xrpl.models.transactions").TrustSet

            tx = TrustSet(
                account=account_address,
                limit_amount=IssuedCurrencyAmount(
                    currency=HeliosConfig.TOKEN_SYMBOL,
                    issuer=self.issuer_address,
                    value=str(limit_value),
                ),
            )
            return self._submit_transaction(tx, account_secret, action="TrustSet")
        except Exception:
            return self._simulate_tx("TrustSet", payload)

    def issue_token_payment(self, destination: str, value: float, memo_text: str = "") -> dict:
        payload = {
            "TransactionType": "Payment",
            "Account": self.issuer_address,
            "Destination": destination,
            "Amount": {
                "currency": HeliosConfig.TOKEN_SYMBOL,
                "issuer": self.issuer_address,
                "value": str(value),
            },
            "Memo": memo_text,
        }
        if not self.is_ready() or not self.issuer_secret:
            return self._simulate_tx("Payment", payload)

        try:
            amounts_mod = importlib.import_module("xrpl.models.amounts")
            tx_mod = importlib.import_module("xrpl.models.transactions")
            IssuedCurrencyAmount = amounts_mod.IssuedCurrencyAmount
            Memo = tx_mod.Memo
            Payment = tx_mod.Payment

            memos = []
            if memo_text:
                memos.append(
                    Memo(
                        memo_data=memo_text.encode("utf-8").hex(),
                        memo_type="746578742F706C61696E",
                    )
                )

            tx = Payment(
                account=self.issuer_address,
                destination=destination,
                amount=IssuedCurrencyAmount(
                    currency=HeliosConfig.TOKEN_SYMBOL,
                    issuer=self.issuer_address,
                    value=str(value),
                ),
                memos=memos or None,
            )
            return self._submit_transaction(tx, self.issuer_secret, action="Payment")
        except Exception:
            return self._simulate_tx("Payment", payload)

    def mint_nft(self, metadata_uri: str, taxon: int,
                 transferable: bool = True) -> dict:
        payload = {
            "TransactionType": "NFTokenMint",
            "Account": self.issuer_address,
            "NFTokenTaxon": taxon,
            "URI": metadata_uri,
            "Flags": 8 if transferable else 0,
            "TransferFee": 0,
        }
        if not self.is_ready() or not self.issuer_secret:
            return self._simulate_tx("NFTokenMint", payload)

        try:
            NFTokenMint = importlib.import_module("xrpl.models.transactions").NFTokenMint

            tx = NFTokenMint(
                account=self.issuer_address,
                nftoken_taxon=taxon,
                uri=metadata_uri.encode("utf-8").hex(),
                flags=8 if transferable else 0,
                transfer_fee=0,
            )
            return self._submit_transaction(tx, self.issuer_secret, action="NFTokenMint")
        except Exception:
            return self._simulate_tx("NFTokenMint", payload)

    def anchor_receipt(self, mvr_id: str, evidence_hash: str, cid: str | None = None) -> dict:
        memo_text = f"{mvr_id}|{evidence_hash}|{cid or ''}".strip("|")
        payload = {
            "TransactionType": "Payment",
            "Account": self.treasury_address,
            "Destination": self.treasury_address,
            "Amount": "0",
            "Memo": memo_text,
        }
        if not self.is_ready() or not self.treasury_secret:
            result = self._simulate_tx("AnchorReceipt", payload)
            result["memo"] = memo_text
            return result

        try:
            tx_mod = importlib.import_module("xrpl.models.transactions")
            Memo = tx_mod.Memo
            Payment = tx_mod.Payment

            tx = Payment(
                account=self.treasury_address,
                destination=self.treasury_address,
                amount="0",
                memos=[
                    Memo(
                        memo_data=memo_text.encode("utf-8").hex(),
                        memo_type="746578742F706C61696E",
                    )
                ],
            )
            result = self._submit_transaction(tx, self.treasury_secret, action="AnchorReceipt")
            result["memo"] = memo_text
            return result
        except Exception:
            result = self._simulate_tx("AnchorReceipt", payload)
            result["memo"] = memo_text
            return result

    def _submit_transaction(self, transaction, wallet_secret: str, action: str) -> dict:
        try:
            JsonRpcClient = importlib.import_module("xrpl.clients").JsonRpcClient
            tx_mod = importlib.import_module("xrpl.transaction")
            Wallet = importlib.import_module("xrpl.wallet").Wallet
            safe_sign_and_autofill_transaction = tx_mod.safe_sign_and_autofill_transaction
            send_reliable_submission = tx_mod.send_reliable_submission

            client = JsonRpcClient(self.node_url)
            wallet = Wallet.from_seed(wallet_secret)
            signed = safe_sign_and_autofill_transaction(transaction, wallet, client)
            response = send_reliable_submission(signed, client)
            result = response.result if hasattr(response, "result") else response
            tx_json = result.get("tx_json", {}) if isinstance(result, dict) else {}
            tx_hash = tx_json.get("hash") or self._hash_payload({"action": action, "fallback": True})
            return {
                "action": action,
                "simulation": False,
                "submitted": True,
                "network": self.network,
                "tx_hash": tx_hash,
                "ledger_result": result.get("engine_result") if isinstance(result, dict) else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            result = self._simulate_tx(action, {"error": str(exc)})
            result["error"] = str(exc)
            return result

    def _simulate_wallet(self, member_id: str) -> dict:
        digest = hashlib.sha256(member_id.encode("utf-8")).hexdigest()
        return {
            "chain": "XRPL",
            "classic_address": f"r{digest[:33]}",
            "seed": digest[:29],
            "simulation": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _simulate_tx(self, action: str, payload: dict) -> dict:
        return {
            "action": action,
            "simulation": True,
            "submitted": False,
            "network": self.network,
            "tx_hash": self._hash_payload({"action": action, "payload": payload}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _hash_payload(payload: dict) -> str:
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest().upper()
