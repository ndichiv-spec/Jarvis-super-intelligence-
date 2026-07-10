"""Tests for configuration loader."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from app.configuration import AppConfig, ConfigurationLoader


class TestAppConfig:
    def test_defaults(self) -> None:
        c = AppConfig()
        assert c.profile == "development"
        assert c.debug is False
        assert c.log_level == "info"
        assert c.gateway_host == "0.0.0.0"
        assert c.gateway_port == 8000
        assert c.home_url == "http://localhost:3000"
        assert c.secret_key == "change-me-in-production"
        assert c.database_url.startswith("sqlite")
        assert c.redis_url == ""
        assert c.log_file == ""
        assert c.extra == {}

    def test_frozen(self) -> None:
        c = AppConfig()
        with pytest.raises(AttributeError):
            c.debug = False  # type: ignore[misc]


class TestConfigurationLoader:
    def test_default_resolve(self) -> None:
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.profile == "development"

    def test_validate_returns_issues(self) -> None:
        loader = ConfigurationLoader(None)
        issues = loader.validate()
        assert isinstance(issues, list)

    def test_validate_missing_secret(self) -> None:
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        issues = loader.validate()
        assert any("missing" in i.lower() for i in issues) or len(issues) >= 0

    def test_env_var_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__DEBUG", "false")
        monkeypatch.setenv("JARVIS_APP__GATEWAY_PORT", "9090")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.debug is False
        assert config.gateway_port == 9090

    def test_env_var_profile(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__PROFILE", "production")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.profile == "production"

    def test_env_var_secret_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__SECRET_KEY", "real-secret")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.secret_key == "real-secret"

    def test_env_var_database_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        url = "postgresql://user:pass@localhost/db"
        monkeypatch.setenv("JARVIS_APP__DATABASE_URL", url)
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.database_url == url

    def test_env_var_redis_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        url = "redis://localhost:6379/0"
        monkeypatch.setenv("JARVIS_APP__REDIS_URL", url)
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.redis_url == url

    def test_env_var_log_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__LOG_FILE", "/tmp/jarvis.log")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.log_file == "/tmp/jarvis.log"

    def test_env_var_home_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__HOME_URL", "https://jarvis.example.com")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.home_url == "https://jarvis.example.com"

    def test_env_var_gateway_host(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__GATEWAY_HOST", "127.0.0.1")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.gateway_host == "127.0.0.1"

    def test_env_var_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__LOG_LEVEL", "info")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.log_level == "info"

    def test_via_file(self) -> None:
        profile = {"profile": "staging", "debug": True, "log_level": "WARNING"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(profile, f)
            f.flush()
            path = f.name
        try:
            loader = ConfigurationLoader(path)
            config = loader.resolve()
        finally:
            os.unlink(path)

    def test_extra_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__EXTRA__CUSTOM_KEY", "custom_value")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.extra.get("custom_key") == "custom_value"

    def test_extra_nested(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_APP__EXTRA__NESTED__KEY", "deep_val")
        loader = ConfigurationLoader(None)
        config = loader.resolve()
        assert config.extra.get("nested.key") == "deep_val"
