"""
Tests for the audit logging system.
"""

import pytest


class TestAuditAction:
    """Audit action enum."""

    def test_actions_are_strings(self):
        from core.audit import AuditAction
        assert AuditAction.TOKEN_MINT_XRPL.value == "token_mint_xrpl"
        assert AuditAction.TOKEN_MINT_EVM.value == "token_mint_evm"
        assert AuditAction.NFT_MINT.value == "nft_mint"

    def test_all_expected_actions_exist(self):
        from core.audit import AuditAction
        expected = [
            "TOKEN_MINT_XRPL", "TOKEN_MINT_EVM", "NFT_MINT",
            "CEREMONIAL_MINT", "SETTLEMENT_START", "SETTLEMENT_COMPLETE",
            "CERTIFICATE_CREATE", "CERTIFICATE_REDEEM", "MEMBER_JOIN",
            "TREASURY_ANCHOR", "IPFS_PIN", "AUTH_FAILURE",
        ]
        for action in expected:
            assert hasattr(AuditAction, action)


class TestIdempotencyKey:
    """Idempotency key generation."""

    def test_deterministic(self):
        from core.audit import generate_idempotency_key
        k1 = generate_idempotency_key("mint", "member-1", "2024-01-01")
        k2 = generate_idempotency_key("mint", "member-1", "2024-01-01")
        assert k1 == k2

    def test_different_inputs_different_keys(self):
        from core.audit import generate_idempotency_key
        k1 = generate_idempotency_key("mint", "member-1")
        k2 = generate_idempotency_key("mint", "member-2")
        assert k1 != k2

    def test_key_length(self):
        from core.audit import generate_idempotency_key
        key = generate_idempotency_key("test", "data")
        assert len(key) == 48


class TestAuditLogModel:
    """AuditLog model basic tests."""

    def test_model_has_required_columns(self):
        from core.audit import AuditLog
        columns = [c.name for c in AuditLog.__table__.columns]
        assert "action" in columns
        assert "actor_id" in columns
        assert "target_id" in columns
        assert "chain" in columns
        assert "tx_hash" in columns
        assert "idempotency_key" in columns
