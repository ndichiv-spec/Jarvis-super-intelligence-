from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


class SecretManagerClient(Protocol):
    async def read_secret(self, name: str) -> str | None: ...


class EnvironmentSecretProviderAdapter(BaseInfrastructureAdapter):
    def __init__(self, *, prefix: str = "JARVIS_SECRET_") -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="secrets.environment",
                version="1.0.0",
                provider="environment",
                capabilities=("secrets", "local"),
                configuration_profile="default",
                compatibility=("secrets:v1",),
            )
        )
        self._prefix = prefix

    async def resolve(self, secret_name: str) -> str | None:
        key = f"{self._prefix}{secret_name.upper()}"
        return os.getenv(key)


class FileSecretProviderAdapter(BaseInfrastructureAdapter):
    def __init__(self, *, file_path: str = "config/secrets.json") -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="secrets.file",
                version="1.0.0",
                provider="local-file",
                capabilities=("secrets", "local"),
                configuration_profile="default",
                compatibility=("secrets:v1",),
            )
        )
        self._file_path = Path(file_path)
        self._secrets: dict[str, str] = {}

    async def start(self) -> None:
        if self._file_path.exists():
            payload = json.loads(self._file_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                self._secrets = {str(name): str(value) for name, value in payload.items()}
        await super().start()

    async def resolve(self, secret_name: str) -> str | None:
        return self._secrets.get(secret_name)


class HashicorpVaultSecretProviderAdapter(BaseInfrastructureAdapter):
    def __init__(self, *, client: SecretManagerClient | None = None) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="secrets.hashicorp_vault",
                version="1.0.0",
                provider="hashicorp-vault",
                capabilities=("secrets", "distributed", "rotation"),
                configuration_profile="default",
                compatibility=("secrets:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError("Vault client is required.")
        await super().start()

    async def resolve(self, secret_name: str) -> str | None:
        if self._client is None:
            raise RuntimeError("Vault client is not configured.")
        return await self._client.read_secret(secret_name)


class CloudSecretManagerAdapter(BaseInfrastructureAdapter):
    def __init__(
        self, *, client: SecretManagerClient | None = None, provider: str = "cloud-secret-manager"
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="secrets.cloud",
                version="1.0.0",
                provider=provider,
                capabilities=("secrets", "distributed", "rotation"),
                configuration_profile="default",
                compatibility=("secrets:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError("Cloud secret manager client is required.")
        await super().start()

    async def resolve(self, secret_name: str) -> str | None:
        if self._client is None:
            raise RuntimeError("Cloud secret manager client is not configured.")
        return await self._client.read_secret(secret_name)
