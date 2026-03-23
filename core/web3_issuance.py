"""
core/web3_issuance.py — Web3 Issuance Engine
==============================================
Handles instant token issuance, NFT certificate minting,
and ceremonial NFT creation for all new members.

Three issuance types on member join:
  1. Instant HLS token delivery to atomic wallet
  2. Gold-backed NFT certificate (membership proof)
  3. Ceremonial NFT (one-time founding artifact)

All issuances are on-chain (XRPL NFTokenMint / Stellar custom ops).
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from config import HeliosConfig
from core.xrpl_bridge import XRPLBridge
from core.ipfs import IpfsBundleService

log = logging.getLogger("helios.issuance")


# ── Constants ──────────────────────────────────────────────────────────
XRPL_ISSUER = HeliosConfig.XRPL_ISSUER_ADDRESS or "rHELIOSxxxxxxxxxxxxxxxxxxxxxxxxxx"
STELLAR_ISSUER = "GHELIOSXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
HLS_CURRENCY_CODE = "HLS"
TOKEN_PRICE_PHASE1 = 0.05   # $0.05 per HLS — founding price
TOKEN_PRICE_PHASE2 = 0.25
TOKEN_PRICE_PHASE3 = 0.50

# NFT metadata URIs (IPFS-backed)
CERT_METADATA_BASE = "ipfs://QmHeliosCertificates/"
CEREMONIAL_METADATA_BASE = "ipfs://QmHeliosCeremonial/"


class TokenIssuance:
    """Instant HLS token delivery to member wallets."""

    @staticmethod
    def calculate_tokens(usd_amount: float, phase: int = 1) -> dict:
        """
        Calculate token allocation at current phase price.
        No bonuses — pure math at $0.05/HLS Phase 1.
        """
        prices = {1: TOKEN_PRICE_PHASE1, 2: TOKEN_PRICE_PHASE2, 3: TOKEN_PRICE_PHASE3}
        price = prices.get(phase, TOKEN_PRICE_PHASE1)
        tokens = usd_amount / price

        return {
            "usd_amount": usd_amount,
            "phase": phase,
            "price_per_hls": price,
            "tokens_issued": tokens,
            "formatted": f"{tokens:,.0f} HLS",
        }

    @staticmethod
    def issue_tokens(member_id: str, xrpl_address: str, amount: float, phase: int = 1) -> dict:
        """
        Issue HLS tokens directly to member's XRPL wallet.
        Uses Payment transaction from the issuing account.
        Tokens arrive in the member's wallet instantly.
        """
        calc = TokenIssuance.calculate_tokens(amount, phase)

        tx = XRPLBridge().issue_token_payment(
            destination=xrpl_address,
            value=calc["tokens_issued"],
            memo_text=f"HLS issuance: {calc['formatted']} at ${calc['price_per_hls']}/HLS"
        )

        return {
            "type": "token_issuance",
            "member_id": member_id,
            "destination": xrpl_address,
            "tokens": calc["tokens_issued"],
            "formatted": calc["formatted"],
            "price": calc["price_per_hls"],
            "phase": phase,
            "chain": "XRPL",
            "tx_hash": tx.get("tx_hash"),
            "status": "issued" if tx.get("submitted") else "simulated",
            "simulation": tx.get("simulation", True),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class NFTCertificate:
    """Gold-backed NFT certificate issuance on XRPL."""

    @staticmethod
    def mint_membership_nft(member_id: str, xrpl_address: str,
                            contract_tier: str, gold_weight_oz: float) -> dict:
        """
        Mint an NFT certificate representing the member's gold-backed
        allocation. Issued on XRPL via NFTokenMint.

        Metadata is pinned to IPFS (Pinata) first when credentials are
        available; otherwise falls back to a deterministic hash-based URI.
        """
        metadata = {
            "name": f"Helios Gold Certificate — {contract_tier}",
            "description": "Gold-backed digital certificate issued by the Helios Protocol",
            "member_id_hash": hashlib.sha256(member_id.encode()).hexdigest()[:16],
            "contract_tier": contract_tier,
            "gold_backing_oz": gold_weight_oz,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "redeemable": True,
            "redemption_options": ["physical_gold", "stablecoin_usdc", "stablecoin_usdt"],
            "chain": "XRPL",
            "standard": "XLS-20",
        }

        # Pin metadata to IPFS before minting
        ipfs = IpfsBundleService()
        pin_result = ipfs.pin_json(metadata, f"cert-{member_id[:12]}")
        if pin_result.get("stored") and pin_result.get("cid"):
            metadata_uri = f"ipfs://{pin_result['cid']}"
            log.info("Cert metadata pinned: %s", metadata_uri)
        else:
            metadata_uri = f"{CERT_METADATA_BASE}{hashlib.sha256(json.dumps(metadata).encode()).hexdigest()[:24]}"
            log.warning("IPFS pin skipped for cert (simulation): %s", pin_result.get("error", "not configured"))

        nft_tx = XRPLBridge().mint_nft(
            metadata_uri=metadata_uri,
            taxon=1,
            transferable=True,
        )

        return {
            "type": "nft_certificate",
            "nft_standard": "XLS-20",
            "member_id": member_id,
            "destination": xrpl_address,
            "contract_tier": contract_tier,
            "gold_backing_oz": gold_weight_oz,
            "metadata_uri": metadata_uri,
            "ipfs_cid": pin_result.get("cid"),
            "metadata_pinned": pin_result.get("stored", False),
            "tx_hash": nft_tx.get("tx_hash"),
            "status": "minted" if nft_tx.get("submitted") else "simulated",
            "simulation": nft_tx.get("simulation", True),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class CeremonialNFT:
    """
    One-time ceremonial NFT for new members.
    Non-transferable. Marks the moment of joining.
    Serves as permanent on-chain proof of founding status.
    """

    CEREMONIAL_TIERS = {
        "founding": {
            "name": "Genesis Flame",
            "description": "Founding member artifact — marks your place in the genesis of Helios",
            "rarity": "Legendary",
            "transferable": False,
            "visual": "golden_flame_animated",
        },
        "member": {
            "name": "Protocol Key",
            "description": "Your permanent key to the Helios Protocol",
            "rarity": "Standard",
            "transferable": False,
            "visual": "silver_key_animated",
        },
        "affiliate": {
            "name": "Network Beacon",
            "description": "Marks your role as a network builder in the Helios ecosystem",
            "rarity": "Rare",
            "transferable": False,
            "visual": "blue_beacon_animated",
        },
    }

    @staticmethod
    def mint_ceremonial(member_id: str, xrpl_address: str,
                        member_type: str = "founding") -> dict:
        """
        Mint a ceremonial NFT for the new member.
        Non-transferable (soulbound). One per member, ever.
        Metadata is pinned to IPFS when Pinata is configured.
        """
        tier = CeremonialNFT.CEREMONIAL_TIERS.get(member_type,
                CeremonialNFT.CEREMONIAL_TIERS["member"])

        metadata = {
            "name": tier["name"],
            "description": tier["description"],
            "rarity": tier["rarity"],
            "member_id_hash": hashlib.sha256(member_id.encode()).hexdigest()[:16],
            "member_type": member_type,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "transferable": tier["transferable"],
            "visual_asset": tier["visual"],
            "chain": "XRPL",
            "standard": "XLS-20",
            "soulbound": True,
        }

        # Pin metadata to IPFS before minting
        ipfs = IpfsBundleService()
        pin_result = ipfs.pin_json(metadata, f"ceremonial-{member_id[:12]}")
        if pin_result.get("stored") and pin_result.get("cid"):
            metadata_uri = f"ipfs://{pin_result['cid']}"
            log.info("Ceremonial metadata pinned: %s", metadata_uri)
        else:
            metadata_uri = f"{CEREMONIAL_METADATA_BASE}{hashlib.sha256(json.dumps(metadata).encode()).hexdigest()[:24]}"

        nft_tx = XRPLBridge().mint_nft(
            metadata_uri=metadata_uri,
            taxon=100,
            transferable=False,
        )

        return {
            "type": "ceremonial_nft",
            "nft_standard": "XLS-20",
            "tier": tier["name"],
            "rarity": tier["rarity"],
            "member_id": member_id,
            "destination": xrpl_address,
            "soulbound": True,
            "metadata_uri": metadata_uri,
            "ipfs_cid": pin_result.get("cid"),
            "metadata_pinned": pin_result.get("stored", False),
            "tx_hash": nft_tx.get("tx_hash"),
            "status": "minted" if nft_tx.get("submitted") else "simulated",
            "simulation": nft_tx.get("simulation", True),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ── Full Issuance Pipeline ────────────────────────────────────────────

def issue_new_member_package(member_id: str, xrpl_address: str,
                              contract_amount: float,
                              member_type: str = "founding",
                              token_rail: str = "XRPL",
                              evm_address: str = None) -> dict:
    """
    Complete Web3 issuance for a new member:
      1. Instant HLS token delivery (XRPL or EVM rail)
      2. Gold-backed NFT certificate (always XRPL — XLS-20)
      3. Ceremonial NFT (always XRPL — soulbound)

    token_rail: "XRPL" (default) or "EVM"
        When "EVM", tokens are minted via the ERC-20 contract instead.
        NFTs remain on XRPL regardless of rail choice.
    """
    # 1. Token issuance — rail-dependent
    if token_rail == "EVM" and evm_address:
        from core.evm_bridge import get_evm_bridge
        calc = TokenIssuance.calculate_tokens(contract_amount, phase=1)
        bridge = get_evm_bridge()
        evm_result = bridge.mint(evm_address, calc["tokens_issued"])

        token_result = {
            "type": "token_issuance",
            "member_id": member_id,
            "destination": evm_address,
            "tokens": calc["tokens_issued"],
            "formatted": calc["formatted"],
            "price": calc["price_per_hls"],
            "phase": 1,
            "chain": "EVM",
            "chain_id": HeliosConfig.EVM_CHAIN_ID,
            "tx_hash": evm_result.get("tx_hash"),
            "status": evm_result.get("status", "simulated"),
            "simulation": evm_result.get("simulation", True),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        log.info("EVM token issuance: %s HLS to %s", calc["formatted"], evm_address)
    else:
        token_result = TokenIssuance.issue_tokens(
            member_id, xrpl_address, contract_amount, phase=1
        )

    # 2. NFT certificate — always XRPL (gold weight based on 15% treasury allocation)
    gold_allocation_usd = contract_amount * 0.15
    gold_oz = gold_allocation_usd / HeliosConfig.GOLD_SPOT_PRICE_USD
    cert_result = NFTCertificate.mint_membership_nft(
        member_id, xrpl_address,
        contract_tier=f"${contract_amount:,.0f}",
        gold_weight_oz=round(gold_oz, 4)
    )

    # 3. Ceremonial NFT — always XRPL
    ceremonial_result = CeremonialNFT.mint_ceremonial(
        member_id, xrpl_address, member_type
    )

    return {
        "member_id": member_id,
        "package": "new_member_issuance",
        "token_rail": token_rail,
        "issuances": [
            token_result,
            cert_result,
            ceremonial_result,
        ],
        "summary": {
            "tokens_issued": token_result["formatted"],
            "token_chain": token_result.get("chain", "XRPL"),
            "nft_certificate": cert_result["contract_tier"],
            "gold_backing": f"{gold_oz:.4f} oz",
            "ceremonial_nft": ceremonial_result["tier"],
            "total_nfts": 2,
            "nft_chain": "XRPL",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Web3 Preferences ──────────────────────────────────────────────────

class Web3Preferences:
    """
    Member-configurable Web3 settings.
    Members choose which chains, assets, and automation they want.
    """

    DEFAULT_PREFERENCES = {
        "primary_chain": "XRPL",
        "secondary_chain": "EVM",
        "auto_stake": False,
        "auto_stake_duration": 90,   # days
        "preferred_stablecoin": "USDC",
        "certificate_format": "nft",  # nft | json | both
        "auto_convert": False,
        "auto_convert_asset": None,  # BTC, ETH, XRP, etc.
        "notification_on_issuance": True,
        "notification_on_allocation": True,
        "identity_public": True,     # .helios identity visibility
        "cross_chain_settlement": True,
        "token_rail": "XRPL",       # XRPL | EVM — which rail to mint on
    }

    AVAILABLE_CHAINS = ["XRPL", "EVM"]
    AVAILABLE_RAILS = ["XRPL", "EVM"]
    AVAILABLE_ASSETS = ["HLS", "XRP", "ETH", "BTC", "USDC", "USDT"]
    CERTIFICATE_FORMATS = ["nft", "json", "both"]
    STAKE_DURATIONS = [30, 90, 180, 365]

    def __init__(self, member_id: str, prefs: dict = None):
        self.member_id = member_id
        self.preferences = {**self.DEFAULT_PREFERENCES, **(prefs or {})}

    def update(self, key: str, value) -> dict:
        """Update a single preference."""
        if key not in self.DEFAULT_PREFERENCES:
            return {"status": "error", "message": f"Unknown preference: {key}"}

        self.preferences[key] = value
        return {
            "status": "updated",
            "key": key,
            "value": value,
            "member_id": self.member_id,
        }

    def get_all(self) -> dict:
        """Return all current preferences."""
        return {
            "member_id": self.member_id,
            "preferences": self.preferences,
            "available_options": {
                "chains": self.AVAILABLE_CHAINS,
                "rails": self.AVAILABLE_RAILS,
                "assets": self.AVAILABLE_ASSETS,
                "certificate_formats": self.CERTIFICATE_FORMATS,
                "stake_durations": self.STAKE_DURATIONS,
            }
        }

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "preferences": self.preferences,
        }
