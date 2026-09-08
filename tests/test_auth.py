"""
Tests for Authentication and Security
======================================
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestAuth:
    """Test authentication module."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        from api.middleware.auth import create_access_token

        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_create_token_with_expiry(self):
        """Test token creation with expiry."""
        from api.middleware.auth import create_access_token
        from datetime import timedelta

        expires = timedelta(hours=1)
        token = create_access_token(data={"sub": "testuser"}, expires_delta=expires)
        assert token is not None

    def test_password_hashing(self):
        """Test password hashing."""
        from api.middleware.auth import hash_password, pwd_context

        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")
        assert pwd_context.verify(password, hashed) == True
        assert pwd_context.verify("wrongpassword", hashed) == False

    def test_password_hash_different(self):
        """Test that hashing same password produces different results."""
        from api.middleware.auth import hash_password

        password = "testpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Should be different due to salt
        assert hash1 != hash2


class TestRBAC:
    """Test role-based access control."""

    def test_rbac_import(self):
        """Test RBAC can be imported."""
        from api.routers.rbac import router

        assert router is not None

    @pytest.mark.asyncio
    async def test_list_roles(self, test_client, auth_headers):
        """Test listing roles."""
        response = await test_client.get(
            "/api/v1/rbac/roles",
            headers=auth_headers,
        )
        assert response.status_code in [200, 403]


class TestAuthAPI:
    """Test auth API endpoints."""

    @pytest.mark.asyncio
    async def test_login_invalid(self, test_client):
        """Test login with invalid credentials."""
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"username": "invalid", "password": "invalid"},
        )
        assert response.status_code in [401, 400]

    @pytest.mark.asyncio
    async def test_register(self, test_client):
        """Test user registration."""
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code in [200, 201, 400]

    @pytest.mark.asyncio
    async def test_logout(self, test_client, auth_headers):
        """Test logout."""
        response = await test_client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
        )
        assert response.status_code in [200, 401]


class TestSecurity:
    """Test security modules."""

    def test_security_module_import(self):
        """Test security module can be imported."""
        from core import security_module

        assert security_module is not None

    def test_enterprise_security_import(self):
        """Test enterprise security can be imported."""
        from core import enterprise_security

        assert enterprise_security is not None


class TestMiddleware:
    """Test custom middleware."""

    def test_auth_middleware_import(self):
        """Test auth middleware can be imported."""
        from api.middleware.auth import AuthMiddleware

        assert AuthMiddleware is not None

    def test_cache_middleware_import(self):
        """Test cache middleware can be imported."""
        from api.middleware.cache import CacheMiddleware

        assert CacheMiddleware is not None

    def test_rate_limit_middleware_import(self):
        """Test rate limit middleware can be imported."""
        from api.middleware.rate_limit import RateLimitMiddleware

        assert RateLimitMiddleware is not None
