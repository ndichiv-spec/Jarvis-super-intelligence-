"""Tests for Configuration Management."""

from jarvis_cloud.config.manager import ConfigurationManager


class TestConfigurationManager:
    def setup_method(self):
        self.mgr = ConfigurationManager()

    def test_load_profile(self):
        profile = self.mgr.load_profile("development")
        assert profile.name == "development"

    def test_resolve_basic(self):
        self.mgr.resolve("development")
        assert self.mgr.get("logging.level") is not None

    def test_validate_development(self):
        issues = self.mgr.validate("development")
        assert isinstance(issues, list)

    def test_validate_production(self):
        issues = self.mgr.validate("production")
        assert isinstance(issues, list)

    def test_default_value(self):
        val = self.mgr.get("nonexistent.key", "default")
        assert val == "default"

    def test_environment_override(self):
        import os
        os.environ["JARVIS_DEVELOPMENT_LOGGING__LEVEL"] = "debug"
        self.mgr.resolve("development")
        val = self.mgr.get("logging.level")
        assert val is not None
        os.environ.pop("JARVIS_DEVELOPMENT_LOGGING__LEVEL", None)
