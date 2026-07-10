"""Configuration Management - centralized with profiles, secrets, and validation."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConfigEntry:
    key: str
    value: Any
    source: str = "default"
    secret: bool = False
    profile: str | None = None


@dataclass(frozen=True)
class ConfigProfile:
    name: str
    entries: dict[str, ConfigEntry] = field(default_factory=dict)
    extends: str | None = None


class ConfigurationManager:
    def __init__(self, profiles_dir: str | Path | None = None) -> None:
        self._profiles: dict[str, ConfigProfile] = {}
        self._loaded: dict[str, ConfigEntry] = {}
        self._profiles_dir = Path(profiles_dir) if profiles_dir else Path("profiles")

    def load_profile(self, name: str) -> ConfigProfile:
        profile = self._profiles.get(name)
        if profile is not None:
            return profile

        file_path = self._profiles_dir / f"{name}.json"
        if file_path.exists():
            data = json.loads(file_path.read_text())
            entries = {}
            for k, v in data.get("config", {}).items():
                entries[k] = ConfigEntry(
                    key=k,
                    value=v.get("value"),
                    source=v.get("source", "file"),
                    secret=v.get("secret", False),
                    profile=name,
                )
            profile = ConfigProfile(
                name=name,
                entries=entries,
                extends=data.get("extends"),
            )
            self._profiles[name] = profile
            return profile

        self._profiles[name] = ConfigProfile(name=name)
        return self._profiles[name]

    def resolve(self, profile_name: str) -> dict[str, ConfigEntry]:
        """Resolve configuration with inheritance and environment overrides."""
        result: dict[str, ConfigEntry] = {}
        profile = self.load_profile(profile_name)

        if profile.extends:
            parent = self.resolve(profile.extends)
            result.update(parent)

        for key, entry in profile.entries.items():
            result[key] = entry

        env_prefix = f"JARVIS_{profile_name.upper()}_"
        for env_key, env_value in os.environ.items():
            if env_key.startswith(env_prefix):
                config_key = env_key[len(env_prefix):].lower().replace("__", ".")
                result[config_key] = ConfigEntry(
                    key=config_key,
                    value=_parse_env_value(env_value),
                    source="environment",
                    secret="SECRET" in env_key or "PASSWORD" in env_key or "TOKEN" in env_key or "KEY" in env_key,
                    profile=profile_name,
                )

        self._loaded = result
        return result

    def get(self, key: str, default: Any = None) -> Any:
        entry = self._loaded.get(key)
        return entry.value if entry else default

    def get_secret(self, key: str) -> str | None:
        entry = self._loaded.get(key)
        if entry and entry.secret:
            return str(entry.value)
        return None

    def validate(self, profile_name: str) -> list[str]:
        issues: list[str] = []
        try:
            config = self.resolve(profile_name)
        except Exception as e:
            return [f"Failed to resolve profile '{profile_name}': {e}"]

        required_keys = [
            "database.url",
            "redis.url",
            "logging.level",
        ]
        for key in required_keys:
            if key not in config:
                issues.append(f"Missing required config: {key}")

        for key, entry in config.items():
            if entry.value is None and not entry.secret:
                issues.append(f"Config key '{key}' has null value")

        return issues

    def export(self, profile_name: str, path: str | Path) -> None:
        config = self.resolve(profile_name)
        output: dict[str, Any] = {}
        for key, entry in config.items():
            if entry.secret:
                output[key] = {"value": "***", "source": entry.source, "secret": True}
            else:
                output[key] = {"value": entry.value, "source": entry.source}
        Path(path).write_text(json.dumps(output, indent=2, default=str))


def _parse_env_value(value: str) -> Any:
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
