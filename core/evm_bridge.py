"""
core/evm_bridge.py — EVM Bridge for Helios ERC-20 Rail
=======================================================
Secondary issuance rail layered beside XRPL.
Uses web3.py to interact with the deployed HeliosToken (ERC-20) contract.

Never replaces XRPL — only supplements it.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from config import HeliosConfig

log = logging.getLogger("helios.evm")

# ABI is loaded from the Hardhat compilation artifact.
# If the artifact doesn't exist yet (contract not compiled), we use a minimal ABI.
_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "contracts" / "HeliosToken.sol" / "HeliosToken.json"

_MINIMAL_ABI = [
    # mint(address,uint256)
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    # balanceOf(address) → uint256
    {"inputs": [{"name": "account", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    # totalSupply() → uint256
    {"inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    # decimals() → uint8
    {"inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
     "stateMutability": "view", "type": "function"},
    # name() → string
    {"inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
    # symbol() → string
    {"inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
    # CAP() → uint256
    {"inputs": [], "name": "CAP", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    # paused() → bool
    {"inputs": [], "name": "paused", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "view", "type": "function"},
    # pause()
    {"inputs": [], "name": "pause", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    # unpause()
    {"inputs": [], "name": "unpause", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    # Transfer event
    {"anonymous": False, "inputs": [
        {"indexed": True, "name": "from", "type": "address"},
        {"indexed": True, "name": "to", "type": "address"},
        {"indexed": False, "name": "value", "type": "uint256"},
    ], "name": "Transfer", "type": "event"},
]


def _load_abi() -> list:
    """Load full ABI from Hardhat artifact, fall back to minimal ABI."""
    if _ARTIFACT_PATH.exists():
        try:
            with open(_ARTIFACT_PATH) as f:
                artifact = json.load(f)
            return artifact["abi"]
        except Exception:
            pass
    return _MINIMAL_ABI


class EVMBridge:
    """
    Adapter for the Helios ERC-20 contract on any EVM chain.
    Auto-detects whether web3.py is installed and credentials are configured.
    Falls back to simulation mode gracefully.
    """

    def __init__(self):
        self.rpc_url = HeliosConfig.EVM_RPC_URL
        self.chain_id = HeliosConfig.EVM_CHAIN_ID
        self.private_key = HeliosConfig.EVM_PRIVATE_KEY
        self.contract_address = HeliosConfig.EVM_CONTRACT_ADDRESS
        self.explorer_url = HeliosConfig.EVM_EXPLORER_URL
        self.enabled = HeliosConfig.EVM_ENABLED
        self._w3 = None
        self._contract = None
        self._account = None

    # ── Connection ────────────────────────────────────────────────

    def _connect(self):
        """Lazy connect to the EVM node via web3.py."""
        if self._w3 is not None:
            return

        try:
            from web3 import Web3
            from web3.middleware import ExtraDataToPOAMiddleware
        except ImportError:
            log.warning("web3 package not installed — EVM bridge in simulation mode")
            return

        if not self.rpc_url:
            return

        self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # PoA middleware for Polygon, BSC, etc.
        try:
            self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        except Exception:
            pass

        if self.private_key:
            self._account = self._w3.eth.account.from_key(self.private_key)

        if self.contract_address and self._w3.is_connected():
            abi = _load_abi()
            self._contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=abi,
            )

    # ── Status ────────────────────────────────────────────────────

    def is_ready(self) -> bool:
        """True if web3 is connected and contract + keys are configured."""
        self._connect()
        return bool(
            self._w3
            and self._w3.is_connected()
            and self._contract
            and self._account
        )

    def status(self) -> dict:
        """Return diagnostic information about the EVM connection."""
        self._connect()
        connected = self._w3.is_connected() if self._w3 else False
        return {
            "enabled": self.enabled,
            "connected": connected,
            "rpc_url": self.rpc_url[:40] + "..." if self.rpc_url and len(self.rpc_url) > 40 else self.rpc_url,
            "chain_id": self.chain_id,
            "contract": self.contract_address or None,
            "account": self._account.address if self._account else None,
            "ready": self.is_ready(),
        }

    # ── Read Operations ───────────────────────────────────────────

    def token_info(self) -> dict:
        """Get on-chain token metadata."""
        if not self.is_ready():
            return self._simulate("token_info", {})

        try:
            name = self._contract.functions.name().call()
            symbol = self._contract.functions.symbol().call()
            decimals = self._contract.functions.decimals().call()
            total_supply = self._contract.functions.totalSupply().call()
            cap = self._contract.functions.CAP().call()
            paused = self._contract.functions.paused().call()

            return {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "total_supply": total_supply / (10 ** decimals),
                "total_supply_raw": str(total_supply),
                "cap": cap / (10 ** decimals),
                "paused": paused,
                "chain_id": self.chain_id,
                "contract": self.contract_address,
                "simulation": False,
            }
        except Exception as exc:
            log.error("EVM token_info failed: %s", exc)
            return self._simulate("token_info", {"error": str(exc)})

    def balance_of(self, address: str) -> dict:
        """Query HLS balance for an EVM address."""
        if not self.is_ready():
            return self._simulate("balance_of", {"address": address})

        try:
            from web3 import Web3
            checksum = Web3.to_checksum_address(address)
            decimals = self._contract.functions.decimals().call()
            raw = self._contract.functions.balanceOf(checksum).call()

            return {
                "address": checksum,
                "balance": raw / (10 ** decimals),
                "balance_raw": str(raw),
                "decimals": decimals,
                "simulation": False,
            }
        except Exception as exc:
            log.error("EVM balance_of failed: %s", exc)
            return self._simulate("balance_of", {"address": address, "error": str(exc)})

    # ── Write Operations ──────────────────────────────────────────

    def mint(self, to_address: str, amount: float) -> dict:
        """
        Mint HLS tokens to an EVM address.
        amount is in human-readable HLS (e.g., 1000.0 = 1000 HLS).

        Only the backend (MINTER_ROLE) can call this.
        Returns tx hash on success, simulation dict on failure/dry-run.
        """
        if not self.is_ready():
            return self._simulate("mint", {"to": to_address, "amount": amount})

        try:
            from web3 import Web3
            checksum = Web3.to_checksum_address(to_address)
            decimals = self._contract.functions.decimals().call()
            raw_amount = int(amount * (10 ** decimals))

            tx = self._contract.functions.mint(checksum, raw_amount).build_transaction({
                "from": self._account.address,
                "nonce": self._w3.eth.get_transaction_count(self._account.address),
                "chainId": self.chain_id,
                "gas": 100_000,
                "maxFeePerGas": self._w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self._w3.to_wei(1, "gwei"),
            })

            signed = self._account.sign_transaction(tx)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            result = {
                "action": "evm_mint",
                "to": checksum,
                "amount": amount,
                "amount_raw": str(raw_amount),
                "tx_hash": receipt.transactionHash.hex(),
                "block": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "minted" if receipt.status == 1 else "failed",
                "chain_id": self.chain_id,
                "explorer_url": f"{self.explorer_url}/tx/0x{receipt.transactionHash.hex()}",
                "simulation": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            log.info("EVM mint success: %s HLS to %s — tx %s", amount, checksum, result["tx_hash"])
            return result

        except Exception as exc:
            log.error("EVM mint failed: %s", exc)
            result = self._simulate("mint", {"to": to_address, "amount": amount})
            result["error"] = str(exc)
            return result

    def get_tx_status(self, tx_hash: str) -> dict:
        """Check transaction status on-chain."""
        if not self.is_ready():
            return self._simulate("tx_status", {"tx_hash": tx_hash})

        try:
            receipt = self._w3.eth.get_transaction_receipt(tx_hash)
            if receipt is None:
                return {"tx_hash": tx_hash, "status": "pending", "simulation": False}

            return {
                "tx_hash": tx_hash,
                "status": "confirmed" if receipt.status == 1 else "failed",
                "block": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "simulation": False,
            }
        except Exception as exc:
            return self._simulate("tx_status", {"tx_hash": tx_hash, "error": str(exc)})

    # ── Simulation Fallback ───────────────────────────────────────

    @staticmethod
    def _simulate(action: str, context: dict) -> dict:
        """Return a simulation result when EVM is not configured/available."""
        import hashlib
        payload = json.dumps({"action": action, **context}, sort_keys=True, default=str)
        fake_hash = hashlib.sha256(payload.encode()).hexdigest().upper()

        return {
            "action": action,
            "simulation": True,
            "submitted": False,
            "tx_hash": fake_hash,
            "message": "EVM bridge not configured — simulation mode",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **{k: v for k, v in context.items() if k != "error"},
        }


# ── Convenience singleton ────────────────────────────────────────────

_bridge_instance: EVMBridge | None = None

def get_evm_bridge() -> EVMBridge:
    """Get or create a singleton EVMBridge instance."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = EVMBridge()
    return _bridge_instance
