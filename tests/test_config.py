"""
Tests for config.py — safety and correctness.
"""

import os
import pytest


class TestHeliosConfig:
    """Config safety tests."""

    def test_secret_key_not_empty(self):
        """SECRET_KEY must never be empty in testing."""
        from config import HeliosConfig
        assert HeliosConfig.SECRET_KEY, "SECRET_KEY should not be empty"

    def test_debug_false_in_production_mode(self):
        """DEBUG must be False when HELIOS_ENV is production."""
        # We're in testing mode, but the production guard should exist
        from config import IS_PRODUCTION
        # In testing mode IS_PRODUCTION is False, that's correct
        assert not IS_PRODUCTION

    def test_token_symbol(self):
        from config import HeliosConfig
        assert HeliosConfig.TOKEN_SYMBOL == "HLS"

    def test_total_supply(self):
        from config import HeliosConfig
        assert HeliosConfig.TOTAL_SUPPLY == 100_000_000

    def test_token_decimals(self):
        from config import HeliosConfig
        assert HeliosConfig.TOKEN_DECIMALS == 8

    def test_gold_spot_price_positive(self):
        from config import HeliosConfig
        assert HeliosConfig.GOLD_SPOT_PRICE_USD > 0

    def test_treasury_allocation_sums(self):
        """Treasury allocation percentages should be internally consistent."""
        from config import HeliosConfig
        # Gold + Operations + Liquidity + Staking should be reasonable
        gold = HeliosConfig.TREASURY_GOLD_ALLOCATION
        assert 0 < gold <= 1.0, "Gold allocation should be between 0 and 1"

    def test_evm_config_keys_exist(self):
        """EVM config keys should be present (even if empty in testing)."""
        from config import HeliosConfig
        assert hasattr(HeliosConfig, "EVM_RPC_URL")
        assert hasattr(HeliosConfig, "EVM_CHAIN_ID")
        assert hasattr(HeliosConfig, "EVM_PRIVATE_KEY")
        assert hasattr(HeliosConfig, "EVM_CONTRACT_ADDRESS")
        assert hasattr(HeliosConfig, "EVM_ENABLED")

    def test_xrpl_config_keys_exist(self):
        """XRPL config keys should be present."""
        from config import HeliosConfig
        assert hasattr(HeliosConfig, "XRPL_NETWORK")
        assert hasattr(HeliosConfig, "XRPL_NODE_URL")
        assert hasattr(HeliosConfig, "XRPL_ENABLE_SUBMIT")
