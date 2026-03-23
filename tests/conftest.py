"""
Shared test fixtures for all Helios tests.
"""

import os
import pytest

# Force testing environment before importing anything else
os.environ["HELIOS_ENV"] = "testing"
os.environ["HELIOS_SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["HELIOS_API_KEY"] = "test-api-key-12345"
os.environ["HELIOS_DATABASE_URL"] = "sqlite://"  # in-memory


@pytest.fixture(scope="session")
def app():
    """Create the Flask app for testing."""
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture(scope="session")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Headers with valid API key."""
    return {"X-API-Key": "test-api-key-12345"}


@pytest.fixture
def bearer_headers():
    """Headers with valid Bearer token."""
    return {"Authorization": "Bearer test-api-key-12345"}
