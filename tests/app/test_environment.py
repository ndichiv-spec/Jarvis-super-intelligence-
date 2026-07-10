"""Tests for environment validator."""

from __future__ import annotations

from app.configuration import AppConfig
from app.environment import EnvCheck, EnvironmentValidator


class TestEnvCheck:
    def test_create(self) -> None:
        c = EnvCheck(name="test", status="ok", message="ok", severity="info")
        assert c.name == "test"
        assert c.status == "ok"


class TestEnvironmentValidator:
    def test_validate_all_returns_list(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        assert isinstance(checks, list)
        assert len(checks) > 0

    def test_python_version_check(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        py_check = [c for c in checks if "python" in c.name.lower()]
        assert len(py_check) > 0
        assert py_check[0].status in ("ok", "error")

    def test_config_check(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        cfg_checks = [c for c in checks if c.name == "configuration"]
        assert len(cfg_checks) > 0

    def test_default_secret_warning(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        secret_checks = [c for c in checks if "secret" in c.message.lower()]
        if secret_checks:
            assert secret_checks[0].status == "warning"

    def test_writable_directories(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        dir_checks = [c for c in checks if "writable" in c.name.lower()]
        assert len(dir_checks) > 0
        for c in dir_checks:
            assert c.status in ("ok", "warning")

    def test_all_check_names_present(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        names = {c.name for c in checks}
        assert "python_version" in names
        assert "writable_dirs" in names
        assert "configuration" in names
        assert "optional_services" in names

    def test_optional_services_check(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        svc_checks = [c for c in checks if c.name == "optional_services"]
        assert len(svc_checks) > 0

    def test_info_check_exists(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        has_info = any(c.severity == "info" for c in checks)
        has_warning = any(c.severity == "warning" for c in checks)
        assert has_info or has_warning

    def test_config_check_default_secret(self) -> None:
        config = AppConfig()
        v = EnvironmentValidator(config)
        checks = v.validate_all()
        config_check = next((c for c in checks if c.name == "configuration"), None)
        assert config_check is not None
        if config.secret_key == "change-me-in-production":
            assert config_check.status == "warning"
