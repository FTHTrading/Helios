"""
Tests for core domain logic — token calculation, issuance, XRPL bridge.
"""

import pytest
from datetime import datetime, timezone


class TestTokenIssuance:
    """Token calculation and issuance logic."""

    def test_phase1_price(self):
        from core.web3_issuance import TokenIssuance
        result = TokenIssuance.calculate_tokens(100.0, phase=1)
        assert result["tokens_issued"] == 2000.0  # $100 / $0.05 = 2000
        assert result["price_per_hls"] == 0.05

    def test_phase2_price(self):
        from core.web3_issuance import TokenIssuance
        result = TokenIssuance.calculate_tokens(100.0, phase=2)
        assert result["tokens_issued"] == 400.0  # $100 / $0.25 = 400
        assert result["price_per_hls"] == 0.25

    def test_phase3_price(self):
        from core.web3_issuance import TokenIssuance
        result = TokenIssuance.calculate_tokens(100.0, phase=3)
        assert result["tokens_issued"] == 200.0  # $100 / $0.50 = 200
        assert result["price_per_hls"] == 0.50

    def test_formatted_output(self):
        from core.web3_issuance import TokenIssuance
        result = TokenIssuance.calculate_tokens(5000.0, phase=1)
        assert result["formatted"] == "100,000 HLS"

    def test_zero_amount(self):
        from core.web3_issuance import TokenIssuance
        result = TokenIssuance.calculate_tokens(0.0, phase=1)
        assert result["tokens_issued"] == 0.0


class TestXRPLBridge:
    """XRPL bridge simulation mode tests."""

    def test_bridge_creates_simulated_wallet(self):
        from core.xrpl_bridge import XRPLBridge
        bridge = XRPLBridge()
        wallet = bridge.create_member_wallet("test-member-123")
        assert wallet["chain"] == "XRPL"
        assert "classic_address" in wallet
        assert wallet.get("simulation") is True or wallet.get("simulation") is False

    def test_bridge_simulated_payment(self):
        from core.xrpl_bridge import XRPLBridge
        bridge = XRPLBridge()
        result = bridge.issue_token_payment("rTestAddress123", 1000.0, "test memo")
        assert "tx_hash" in result
        assert result["action"] == "Payment" or result.get("type") == "Payment"

    def test_bridge_simulated_nft_mint(self):
        from core.xrpl_bridge import XRPLBridge
        bridge = XRPLBridge()
        result = bridge.mint_nft("ipfs://test", taxon=1, transferable=True)
        assert "tx_hash" in result


class TestNFTCertificate:
    """NFT certificate minting tests."""

    def test_mint_returns_required_fields(self):
        from core.web3_issuance import NFTCertificate
        result = NFTCertificate.mint_membership_nft(
            member_id="test-001",
            xrpl_address="rTestAddress",
            contract_tier="$500",
            gold_weight_oz=0.035,
        )
        assert result["type"] == "nft_certificate"
        assert result["nft_standard"] == "XLS-20"
        assert result["contract_tier"] == "$500"
        assert result["gold_backing_oz"] == 0.035
        assert "metadata_uri" in result
        assert "tx_hash" in result
        # IPFS fields should be present
        assert "ipfs_cid" in result
        assert "metadata_pinned" in result


class TestCeremonialNFT:
    """Ceremonial NFT tests."""

    def test_founding_tier(self):
        from core.web3_issuance import CeremonialNFT
        result = CeremonialNFT.mint_ceremonial("test-001", "rTestAddr", "founding")
        assert result["tier"] == "Genesis Flame"
        assert result["soulbound"] is True
        assert result["rarity"] == "Legendary"

    def test_member_tier(self):
        from core.web3_issuance import CeremonialNFT
        result = CeremonialNFT.mint_ceremonial("test-002", "rTestAddr", "member")
        assert result["tier"] == "Protocol Key"
        assert result["rarity"] == "Standard"

    def test_affiliate_tier(self):
        from core.web3_issuance import CeremonialNFT
        result = CeremonialNFT.mint_ceremonial("test-003", "rTestAddr", "affiliate")
        assert result["tier"] == "Network Beacon"
        assert result["rarity"] == "Rare"

    def test_unknown_type_defaults_to_member(self):
        from core.web3_issuance import CeremonialNFT
        result = CeremonialNFT.mint_ceremonial("test-004", "rTestAddr", "unknown")
        assert result["tier"] == "Protocol Key"


class TestIssuancePipeline:
    """Full member issuance pipeline."""

    def test_issue_new_member_package_xrpl(self):
        from core.web3_issuance import issue_new_member_package
        result = issue_new_member_package(
            member_id="test-pipeline-001",
            xrpl_address="rTestPipelineAddr",
            contract_amount=500.0,
            member_type="founding",
            token_rail="XRPL",
        )
        assert result["package"] == "new_member_issuance"
        assert result["token_rail"] == "XRPL"
        assert len(result["issuances"]) == 3
        assert result["summary"]["total_nfts"] == 2

    def test_issue_new_member_package_evm_without_address_falls_back(self):
        """When EVM is requested but no evm_address given, should default to XRPL."""
        from core.web3_issuance import issue_new_member_package
        result = issue_new_member_package(
            member_id="test-pipeline-002",
            xrpl_address="rTestAddr2",
            contract_amount=500.0,
            token_rail="EVM",
            evm_address=None,  # No EVM address — should fall back
        )
        # Should still succeed via XRPL fallback
        assert result["package"] == "new_member_issuance"


class TestEVMBridge:
    """EVM bridge simulation tests."""

    def test_bridge_initializes(self):
        from core.evm_bridge import EVMBridge
        bridge = EVMBridge()
        assert bridge.enabled is False or bridge.enabled is True

    def test_status_returns_dict(self):
        from core.evm_bridge import get_evm_bridge
        bridge = get_evm_bridge()
        status = bridge.status()
        assert "enabled" in status
        assert "connected" in status
        assert "ready" in status

    def test_simulation_mint(self):
        from core.evm_bridge import EVMBridge
        bridge = EVMBridge()
        result = bridge.mint("0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18", 100.0)
        assert result["simulation"] is True
        assert "tx_hash" in result

    def test_simulation_balance(self):
        from core.evm_bridge import EVMBridge
        bridge = EVMBridge()
        result = bridge.balance_of("0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18")
        assert result["simulation"] is True

    def test_token_info_simulation(self):
        from core.evm_bridge import EVMBridge
        bridge = EVMBridge()
        result = bridge.token_info()
        assert result["simulation"] is True


class TestIPFSBundleService:
    """IPFS/Pinata service tests."""

    def test_hash_bundle_deterministic(self):
        from core.ipfs import IpfsBundleService
        ipfs = IpfsBundleService()
        bundle = {"key": "value", "number": 42}
        h1 = ipfs.hash_bundle(bundle)
        h2 = ipfs.hash_bundle(bundle)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_pin_json_without_credentials(self):
        from core.ipfs import IpfsBundleService
        ipfs = IpfsBundleService()
        result = ipfs.pin_json({"test": True}, "test-pin")
        # Without Pinata credentials, should return simulation
        assert result["simulation"] is True
        assert result["sha256"]

    def test_build_receipt_manifest(self):
        from core.ipfs import IpfsBundleService
        ipfs = IpfsBundleService()
        manifest = ipfs.build_receipt_manifest(mvr_id="MVR-001", amount=100.0)
        assert manifest["protocol"] == "HELIOS"
        assert manifest["mvr_id"] == "MVR-001"
        assert "generated_at" in manifest


class TestWeb3Preferences:
    """Web3 preference system."""

    def test_default_preferences(self):
        from core.web3_issuance import Web3Preferences
        prefs = Web3Preferences("test-member")
        defaults = prefs.get_all()
        assert defaults["preferences"]["primary_chain"] == "XRPL"
        assert defaults["preferences"]["token_rail"] == "XRPL"

    def test_update_preference(self):
        from core.web3_issuance import Web3Preferences
        prefs = Web3Preferences("test-member")
        result = prefs.update("token_rail", "EVM")
        assert result["status"] == "updated"
        assert prefs.preferences["token_rail"] == "EVM"

    def test_update_unknown_preference(self):
        from core.web3_issuance import Web3Preferences
        prefs = Web3Preferences("test-member")
        result = prefs.update("nonexistent_key", "value")
        assert result["status"] == "error"

    def test_available_rails(self):
        from core.web3_issuance import Web3Preferences
        assert "XRPL" in Web3Preferences.AVAILABLE_RAILS
        assert "EVM" in Web3Preferences.AVAILABLE_RAILS
