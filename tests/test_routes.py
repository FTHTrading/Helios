"""
Tests for page routes and API endpoints.
"""

import pytest


class TestPageRoutes:
    """Verify all page routes return 200."""

    PAGES = [
        "/",
        "/health",
        "/activate",
        "/guide",
        "/treasury",
        "/vault/gold",
        "/metrics",
        "/token-offering",
        "/ask",
        "/status",
    ]

    @pytest.mark.parametrize("path", PAGES)
    def test_page_returns_200(self, client, path):
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"


class TestHealthEndpoints:
    """Verify health check structure."""

    def test_health_returns_json(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["version"] == "3.0.0"
        assert data["system"] == "helios"

    def test_api_health_same_as_health(self, client):
        resp = client.get("/api/health")
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_readiness_probe(self, client):
        resp = client.get("/api/infra/readiness")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["success"] is True


class TestAPIEndpoints:
    """Verify core API routes respond correctly."""

    API_GET_ROUTES = [
        "/api/funding/catalog",
        "/api/infra/readiness",
        "/api/treasury/receipts",
        "/api/treasury/reserves",
        "/api/token/pools",
        "/api/token/info",
        "/api/energy/map",
        "/api/token/supply",
    ]

    @pytest.mark.parametrize("path", API_GET_ROUTES)
    def test_api_get_returns_200(self, client, path, bearer_headers):
        resp = client.get(path, headers=bearer_headers)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"

    def test_identity_verify(self, client, bearer_headers):
        resp = client.get("/api/identity/verify/test-helios-id", headers=bearer_headers)
        # May be 200 or 404 (member not found) — just not a route error
        assert resp.status_code in (200, 404)

    def test_integrations_endpoint(self, client, bearer_headers):
        resp = client.get("/api/infra/status", headers=bearer_headers)
        assert resp.status_code == 200


class TestEVMEndpoints:
    """Verify EVM API routes exist and respond."""

    def test_evm_status(self, client):
        resp = client.get("/api/evm/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_evm_token_info(self, client):
        resp = client.get("/api/evm/token")
        assert resp.status_code == 200

    def test_evm_validate_valid_address(self, client):
        resp = client.get("/api/evm/validate/0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"]["valid"] is True

    def test_evm_validate_invalid_address(self, client):
        resp = client.get("/api/evm/validate/not-an-address")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"]["valid"] is False

    def test_evm_mint_requires_auth(self, client):
        resp = client.post("/api/evm/mint",
                           json={"to": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18", "amount": 100})
        # Should fail without auth
        assert resp.status_code in (401, 503)

    def test_evm_balance_returns(self, client):
        resp = client.get("/api/evm/balance/0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18")
        assert resp.status_code == 200
