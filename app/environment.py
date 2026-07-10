"""Environment Validator — verify Python, packages, writable dirs, services."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import app.configuration as configuration_mod


@dataclass(frozen=True, slots=True)
class EnvCheck:
    name: str = ""
    status: str = "ok"
    message: str = ""
    severity: str = "warning"


class EnvironmentValidator:
    def __init__(self, config: configuration_mod.AppConfig | None = None) -> None:
        self._config = config

    def validate_all(self) -> list[EnvCheck]:
        checks: list[EnvCheck] = []
        checks.append(self._check_python_version())
        checks.append(self._check_writable_dirs())
        checks.append(self._check_config())
        checks.append(self._check_optional_services())
        return checks

    def _check_python_version(self) -> EnvCheck:
        major, minor = sys.version_info.major, sys.version_info.minor
        if major < 3 or (major == 3 and minor < 13):
            return EnvCheck(
                name="python_version",
                status="error",
                message=f"Python 3.13+ required, got {major}.{minor}",
                severity="critical",
            )
        return EnvCheck(name="python_version", status="ok", message=f"Python {major}.{minor}.{sys.version_info.micro}")

    def _check_writable_dirs(self) -> EnvCheck:
        if not self._config:
            return EnvCheck(name="writable_dirs", status="warning", message="No config loaded")
        dirs = [self._config.data_dir, self._config.plugins_dir, self._config.config_dir]
        writable = 0
        for d in dirs:
            p = Path(d)
            try:
                p.mkdir(parents=True, exist_ok=True)
                test_file = p / ".jarvis_write_test"
                test_file.write_text("")
                test_file.unlink()
                writable += 1
            except (OSError, PermissionError):
                pass
        if writable < len(dirs):
            return EnvCheck(
                name="writable_dirs",
                status="warning",
                message=f"{writable}/{len(dirs)} required directories writable",
            )
        return EnvCheck(name="writable_dirs", status="ok", message=f"All {len(dirs)} directories writable")

    def _check_config(self) -> EnvCheck:
        if not self._config:
            return EnvCheck(name="configuration", status="error", message="Configuration not loaded", severity="critical")
        if self._config.secret_key == "change-me-in-production":
            return EnvCheck(name="configuration", status="warning", message="Default secret key in use")
        return EnvCheck(name="configuration", status="ok", message="Configuration valid")

    def _check_optional_services(self) -> EnvCheck:
        if not self._config:
            return EnvCheck(name="optional_services", status="warning", message="No config loaded")
        optional: list[str] = []
        if self._config.redis_url:
            optional.append("redis")
        if self._config.qdrant_url:
            optional.append("qdrant")
        return EnvCheck(name="optional_services", status="ok", message=f"Optional services configured: {', '.join(optional) or 'none'}")
