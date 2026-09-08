"""
JARVIS Test Configuration
==========================
Pytest fixtures and configuration for test suite.
"""

import os
import asyncio

import pytest


# Test configuration
TEST_DB_URL = "sqlite+aiosqlite:///./test_jarvis.db"


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    from unittest.mock import Mock

    config = Mock()
    config.APP_NAME = "JARVIS Test"
    config.APP_VERSION = "0.1.0"
    config.DATABASE_URL = TEST_DB_URL
    config.API_PREFIX = "/api/v1"
    config.DEBUG = True
    config.LOG_LEVEL = "DEBUG"
    config.RATE_LIMIT_REQUESTS = 100
    config.RATE_LIMIT_PERIOD = 60
    config.CORS_ORIGINS = ["*"]
    config.CORS_ALLOW_CREDENTIALS = True
    config.CORS_ALLOW_METHODS = ["*"]
    config.CORS_ALLOW_HEADERS = ["*"]
    return config


@pytest.fixture
async def test_client():
    """Create test HTTP client."""
    from httpx import AsyncClient, ASGITransport
    from api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_ai_response():
    """Mock AI response data."""
    return {
        "response": "Test response",
        "model": "test-model",
        "confidence": 0.95,
        "tokens_used": 10,
    }


@pytest.fixture
def mock_search_results():
    """Mock search results."""
    return [
        {
            "title": "Test Result 1",
            "url": "https://example.com/1",
            "snippet": "Test snippet 1",
            "score": 0.9,
        },
        {
            "title": "Test Result 2",
            "url": "https://example.com/2",
            "snippet": "Test snippet 2",
            "score": 0.8,
        },
    ]


@pytest.fixture
def auth_token():
    """Create test auth token."""
    from api.middleware.auth import create_access_token

    return create_access_token(data={"sub": "testuser", "user_id": "test-id"})


@pytest.fixture
def auth_headers(auth_token):
    """Auth headers for requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Cleanup test database after tests (if available)."""
    yield
    try:
        from core.database import close_db
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(close_db())
        finally:
            loop.close()
    except (ImportError, AttributeError):
        pass

    db_path = "./test_jarvis.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass


@pytest.fixture
def sample_knowledge():
    """Sample knowledge entry."""
    return {
        "key": "test_key",
        "value": "test_value",
        "category": "test",
        "tags": ["test", "sample"],
    }


@pytest.fixture
def sample_agent():
    """Sample agent config."""
    return {
        "name": "test_agent",
        "type": "chat",
        "config": {"model": "default"},
    }
