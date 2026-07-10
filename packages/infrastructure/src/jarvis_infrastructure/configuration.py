from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import cast


class ConfigurationValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SecretReference:
    name: str
    provider: str | None = None

    @classmethod
    def parse(cls, value: str) -> SecretReference:
        if ":" in value:
            provider, name = value.split(":", maxsplit=1)
            return cls(name=name.strip(), provider=provider.strip())
        return cls(name=value.strip())


@dataclass(frozen=True, slots=True)
class AdapterConfiguration:
    identifier: str
    provider: str
    enabled: bool
    profile: str
    settings: Mapping[str, str]
    dependencies: tuple[str, ...]
    secret_references: tuple[SecretReference, ...]

    @classmethod
    def create(
        cls,
        identifier: str,
        provider: str,
        *,
        enabled: bool = True,
        profile: str = "default",
        settings: Mapping[str, str] | None = None,
        dependencies: tuple[str, ...] = (),
        secret_references: tuple[SecretReference, ...] = (),
    ) -> AdapterConfiguration:
        return cls(
            identifier=identifier,
            provider=provider,
            enabled=enabled,
            profile=profile,
            settings=MappingProxyType(dict(settings or {})),
            dependencies=dependencies,
            secret_references=secret_references,
        )


@dataclass(frozen=True, slots=True)
class InfrastructureConfiguration:
    profile: str
    adapters: Mapping[str, AdapterConfiguration]

    @classmethod
    def create(
        cls,
        *,
        profile: str,
        adapters: Mapping[str, AdapterConfiguration] | None = None,
    ) -> InfrastructureConfiguration:
        return cls(
            profile=profile,
            adapters=MappingProxyType(dict(adapters or {})),
        )


class ConfigurationSource:
    def load(self, profile: str | None = None) -> Mapping[str, object]:
        raise NotImplementedError


class EnvironmentConfigurationSource(ConfigurationSource):
    def __init__(self, *, prefix: str = "JARVIS_INFRASTRUCTURE_") -> None:
        self._prefix = prefix

    def load(self, profile: str | None = None) -> Mapping[str, object]:
        resolved_profile = profile or os.getenv(f"{self._prefix}PROFILE", "default")
        adapters: dict[str, dict[str, object]] = {}
        for key, value in os.environ.items():
            if not key.startswith(f"{self._prefix}ADAPTER__"):
                continue
            suffix = key.removeprefix(self._prefix)
            parts = suffix.split("__")
            if len(parts) < 3:
                continue
            _, adapter_id, field, *extra = parts
            entry = adapters.setdefault(adapter_id.lower(), {})
            normalized_field = field.upper()
            if normalized_field == "PROVIDER":
                entry["provider"] = value
            elif normalized_field == "ENABLED":
                entry["enabled"] = value.strip().lower() in {"1", "true", "yes", "on"}
            elif normalized_field == "DEPENDENCIES":
                deps = tuple(item.strip() for item in value.split(",") if item.strip())
                entry["dependencies"] = deps
            elif normalized_field == "SECRETS":
                secrets = tuple(
                    SecretReference.parse(item.strip()) for item in value.split(",") if item.strip()
                )
                entry["secret_references"] = secrets
            elif normalized_field == "SETTINGS" and extra:
                existing_settings = entry.get("settings")
                if isinstance(existing_settings, dict):
                    settings_map = {
                        str(key): str(raw_value)
                        for key, raw_value in existing_settings.items()
                    }
                else:
                    settings_map = {}
                settings_map["__".join(extra).lower()] = value
                entry["settings"] = settings_map

        return {
            "profile": resolved_profile,
            "adapters": adapters,
        }


class FileConfigurationSource(ConfigurationSource):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def load(self, profile: str | None = None) -> Mapping[str, object]:
        if not self._path.exists():
            return {}
        with self._path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ConfigurationValidationError(
                "Configuration file must contain an object at the root."
            )
        if profile and "profiles" in data:
            profiles = data["profiles"]
            if not isinstance(profiles, dict):
                raise ConfigurationValidationError(
                    "'profiles' must be a mapping in configuration file."
                )
            profile_data = profiles.get(profile, {})
            if not isinstance(profile_data, dict):
                raise ConfigurationValidationError("Profile configuration must be a mapping.")
            return profile_data
        return data


class ConfigurationLoader:
    def __init__(self, sources: tuple[ConfigurationSource, ...]) -> None:
        self._sources = sources

    def load(self, *, profile: str | None = None) -> InfrastructureConfiguration:
        merged: dict[str, object] = {}
        for source in self._sources:
            payload = source.load(profile)
            merged = _deep_merge(merged, payload)

        resolved_profile = str(merged.get("profile") or profile or "default")
        adapters_payload = merged.get("adapters", {})
        if not isinstance(adapters_payload, dict):
            raise ConfigurationValidationError("'adapters' configuration must be a mapping.")

        adapters: dict[str, AdapterConfiguration] = {}
        for identifier, value in adapters_payload.items():
            if not isinstance(identifier, str):
                raise ConfigurationValidationError("Adapter identifier must be a string.")
            if not isinstance(value, dict):
                raise ConfigurationValidationError(
                    f"Adapter '{identifier}' configuration must be a mapping."
                )
            provider = str(value.get("provider") or "").strip()
            if not provider:
                raise ConfigurationValidationError(f"Adapter '{identifier}' provider is required.")
            settings = value.get("settings", {})
            if not isinstance(settings, dict):
                raise ConfigurationValidationError(
                    f"Adapter '{identifier}' settings must be a mapping."
                )
            settings_map = {str(key): str(raw_value) for key, raw_value in settings.items()}
            dependencies_raw = value.get("dependencies", ())
            dependencies = _as_tuple(dependencies_raw)
            secret_refs_raw = value.get("secret_references", value.get("secrets", ()))
            secret_references = _parse_secret_references(secret_refs_raw)
            adapters[identifier] = AdapterConfiguration.create(
                identifier=identifier,
                provider=provider,
                enabled=bool(value.get("enabled", True)),
                profile=resolved_profile,
                settings=settings_map,
                dependencies=dependencies,
                secret_references=secret_references,
            )

        return InfrastructureConfiguration.create(profile=resolved_profile, adapters=adapters)


def _deep_merge(base: dict[str, object], update: Mapping[str, object]) -> dict[str, object]:
    result: dict[str, object] = dict(base)
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            existing = cast(dict[str, object], result[key])
            result[key] = _deep_merge(existing, value)
        else:
            result[key] = value
    return result


def _as_tuple(raw_value: object) -> tuple[str, ...]:
    if raw_value is None:
        return ()
    if isinstance(raw_value, str):
        return tuple(item.strip() for item in raw_value.split(",") if item.strip())
    if isinstance(raw_value, list | tuple):
        return tuple(str(item).strip() for item in raw_value if str(item).strip())
    raise ConfigurationValidationError(
        "Dependencies value must be a list, tuple, or comma-separated string."
    )


def _parse_secret_references(raw_value: object) -> tuple[SecretReference, ...]:
    if raw_value is None:
        return ()
    if isinstance(raw_value, str):
        values = [item.strip() for item in raw_value.split(",") if item.strip()]
    elif isinstance(raw_value, list | tuple):
        values = [str(item).strip() for item in raw_value if str(item).strip()]
    else:
        raise ConfigurationValidationError(
            "Secret references must be a list, tuple, or comma-separated string."
        )
    return tuple(SecretReference.parse(value) for value in values)
