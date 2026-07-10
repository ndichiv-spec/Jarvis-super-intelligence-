"""Configuration Loader — layered config from env, .env, profiles, and defaults."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ConfigEntry:
    key: str = ""
    value: Any = None
    source: str = "default"
    secret: bool = False


@dataclass(frozen=True, slots=True)
class AppConfig:
    debug: bool = False
    log_level: str = "info"
    log_file: str = ""
    profile: str = "development"
    home_url: str = "http://localhost:3000"
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8000
    data_dir: str = "data"
    plugins_dir: str = "plugins"
    config_dir: str = "config"
    database_url: str = "sqlite:///data/jarvis.db"
    redis_url: str = ""
    qdrant_url: str = "http://localhost:6333"
    secret_key: str = "change-me-in-production"
    extra: dict[str, Any] = field(default_factory=dict)


class ConfigurationLoader:
    """Layered configuration: system defaults → .env → profile → environment."""

    def __init__(self, root: str | Path | None = None) -> None:
        self._root = Path(root) if root else Path.cwd()
        self._entries: dict[str, ConfigEntry] = {}
        self._resolved: AppConfig | None = None

    def load_defaults(self) -> None:
        self._entries["app.debug"] = ConfigEntry(key="app.debug", value=False, source="default")
        self._entries["app.log_level"] = ConfigEntry(key="app.log_level", value="info", source="default")
        self._entries["app.profile"] = ConfigEntry(key="app.profile", value="development", source="default")
        self._entries["app.gateway_port"] = ConfigEntry(key="app.gateway_port", value=8000, source="default")
        self._entries["app.home_url"] = ConfigEntry(key="app.home_url", value="http://localhost:3000", source="default")
        self._entries["app.gateway_host"] = ConfigEntry(key="app.gateway_host", value="0.0.0.0", source="default")
        self._entries["app.data_dir"] = ConfigEntry(key="app.data_dir", value="data", source="default")
        self._entries["app.database_url"] = ConfigEntry(key="app.database_url", value="sqlite:///data/jarvis.db", source="default")
        self._entries["app.redis_url"] = ConfigEntry(key="app.redis_url", value="", source="default")
        self._entries["app.qdrant_url"] = ConfigEntry(key="app.qdrant_url", value="http://localhost:6333", source="default")
        self._entries["app.secret_key"] = ConfigEntry(key="app.secret_key", value="change-me-in-production", source="default", secret=True)

    def load_dotenv(self, path: str | Path | None = None) -> None:
        env_file = Path(path) if path else self._root / ".env"
        if not env_file.exists():
            return
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("\"'")
            config_key = key.lower().replace("_", ".")
            if config_key not in self._entries:
                continue
            self._entries[config_key] = ConfigEntry(key=config_key, value=value, source=".env")

    def load_profile(self, name: str | None = None) -> None:
        profile_name = name or os.environ.get("JARVIS_PROFILE", "development")
        profile_path = self._root / "profiles" / f"{profile_name}.json"
        if not profile_path.exists():
            return
        data = json.loads(profile_path.read_text(encoding="utf-8"))
        for k, v in data.get("config", {}).items():
            config_key = k.lower()
            self._entries[config_key] = ConfigEntry(
                key=config_key,
                value=v.get("value"),
                source=f"profile:{profile_name}",
                secret=v.get("secret", False),
            )

    def load_environment(self) -> None:
        prefix = "JARVIS_"
        for env_key, env_value in os.environ.items():
            if env_key.startswith(prefix):
                config_key = env_key[len(prefix):].lower().replace("__", ".")
                self._entries[config_key] = ConfigEntry(
                    key=config_key,
                    value=_parse_value(env_value),
                    source="environment",
                    secret="SECRET" in env_key or "KEY" in env_key or "TOKEN" in env_key or "PASSWORD" in env_key,
                )

    def resolve(self) -> AppConfig:
        self.load_defaults()
        self.load_dotenv()
        self.load_profile()
        self.load_environment()
        extra: dict[str, Any] = {}
        for key, entry in self._entries.items():
            if key.startswith("app.extra."):
                extra_key = key[len("app.extra."):]
                extra[extra_key] = entry.value
        self._resolved = AppConfig(
            debug=self._bool("app.debug"),
            log_level=self._str("app.log_level"),
            log_file=self._str("app.log_file"),
            profile=self._str("app.profile"),
            home_url=self._str("app.home_url"),
            gateway_host=self._str("app.gateway_host"),
            gateway_port=self._int("app.gateway_port"),
            data_dir=self._str("app.data_dir"),
            plugins_dir=self._str("app.plugins_dir"),
            config_dir=self._str("app.config_dir"),
            database_url=self._str("app.database_url"),
            redis_url=self._str("app.redis_url"),
            qdrant_url=self._str("app.qdrant_url"),
            secret_key=self._str("app.secret_key"),
            extra=extra,
        )
        return self._resolved

    def get(self, key: str, default: Any = None) -> Any:
        entry = self._entries.get(key)
        return entry.value if entry else default

    def validate(self) -> list[str]:
        issues: list[str] = []
        required = ["app.debug", "app.log_level", "app.profile", "app.database_url"]
        for key in required:
            if key not in self._entries:
                issues.append(f"Missing required config: {key}")
        return issues

    def _str(self, key: str) -> str:
        val = self.get(key)
        return str(val) if val is not None else ""

    def _int(self, key: str) -> int:
        try:
            return int(self.get(key, 0))
        except (ValueError, TypeError):
            return 0

    def _bool(self, key: str) -> bool:
        val = self.get(key, False)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ("true", "yes", "1")
        return bool(val)


def _parse_value(value: str) -> Any:
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
