from __future__ import annotations

import json

import pytest
from jarvis_infrastructure.configuration import (
    ConfigurationLoader,
    ConfigurationValidationError,
    EnvironmentConfigurationSource,
    FileConfigurationSource,
)


def test_environment_configuration_source_reads_adapter_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JARVIS_INFRASTRUCTURE_PROFILE", "dev")
    monkeypatch.setenv("JARVIS_INFRASTRUCTURE_ADAPTER__cache.redis__PROVIDER", "redis")
    monkeypatch.setenv("JARVIS_INFRASTRUCTURE_ADAPTER__cache.redis__ENABLED", "true")
    monkeypatch.setenv("JARVIS_INFRASTRUCTURE_ADAPTER__cache.redis__SETTINGS__host", "localhost")
    monkeypatch.setenv(
        "JARVIS_INFRASTRUCTURE_ADAPTER__cache.redis__DEPENDENCIES", "secrets.environment"
    )
    monkeypatch.setenv("JARVIS_INFRASTRUCTURE_ADAPTER__cache.redis__SECRETS", "env:redis_password")

    source = EnvironmentConfigurationSource()
    loaded = source.load()

    assert loaded["profile"] == "dev"
    adapters = loaded["adapters"]
    assert isinstance(adapters, dict)
    redis_config = adapters["cache.redis"]
    assert redis_config["provider"] == "redis"
    assert redis_config["enabled"] is True
    assert redis_config["settings"] == {"host": "localhost"}
    assert redis_config["dependencies"] == ("secrets.environment",)


def test_file_configuration_source_reads_profile_data(tmp_path) -> None:
    file_path = tmp_path / "infra.json"
    file_path.write_text(
        json.dumps(
            {
                "profiles": {
                    "test": {
                        "adapters": {
                            "database.sqlite": {
                                "provider": "sqlite",
                                "settings": {"path": ":memory:"},
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    source = FileConfigurationSource(file_path)
    payload = source.load(profile="test")

    assert payload["adapters"]["database.sqlite"]["provider"] == "sqlite"


def test_configuration_loader_validates_provider(tmp_path) -> None:
    file_path = tmp_path / "infra-invalid.json"
    file_path.write_text(
        json.dumps(
            {
                "adapters": {
                    "cache.redis": {
                        "enabled": True,
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    loader = ConfigurationLoader((FileConfigurationSource(file_path),))

    with pytest.raises(ConfigurationValidationError):
        loader.load(profile="test")


def test_configuration_loader_builds_typed_configuration(tmp_path) -> None:
    file_path = tmp_path / "infra.json"
    file_path.write_text(
        json.dumps(
            {
                "profile": "integration",
                "adapters": {
                    "database.sqlite": {
                        "provider": "sqlite",
                        "enabled": True,
                        "dependencies": ["secrets.file"],
                        "settings": {"path": "db.sqlite"},
                        "secrets": ["file:db_password"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    loader = ConfigurationLoader((FileConfigurationSource(file_path),))
    configuration = loader.load()

    adapter_config = configuration.adapters["database.sqlite"]
    assert configuration.profile == "integration"
    assert adapter_config.provider == "sqlite"
    assert adapter_config.dependencies == ("secrets.file",)
    assert adapter_config.settings["path"] == "db.sqlite"
    assert adapter_config.secret_references[0].provider == "file"
