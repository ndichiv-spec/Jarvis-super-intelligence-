from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


class ObjectStorageClient(Protocol):
    async def put_object(
        self, key: str, payload: bytes, *, content_type: str | None = None
    ) -> str: ...

    async def get_object(self, key: str) -> bytes: ...

    async def delete_object(self, key: str) -> None: ...

    async def list_objects(self, prefix: str = "") -> tuple[str, ...]: ...


class LocalObjectStorageAdapter(BaseInfrastructureAdapter):
    def __init__(self, *, root: str = ".jarvis-storage") -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="storage.local",
                version="1.0.0",
                provider="local",
                capabilities=("object-storage", "filesystem"),
                configuration_profile="default",
                compatibility=("object-storage:v1",),
            )
        )
        self._root = Path(root)

    async def start(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        await super().start()

    async def put_object(self, key: str, payload: bytes, *, content_type: str | None = None) -> str:
        path = self._resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        metadata_path = path.with_suffix(path.suffix + ".meta")
        if content_type is not None:
            metadata_path.write_text(content_type, encoding="utf-8")
        return str(path)

    async def get_object(self, key: str) -> bytes:
        return self._resolve_path(key).read_bytes()

    async def delete_object(self, key: str) -> None:
        path = self._resolve_path(key)
        if path.exists():
            path.unlink()
        metadata_path = path.with_suffix(path.suffix + ".meta")
        if metadata_path.exists():
            metadata_path.unlink()

    async def list_objects(self, prefix: str = "") -> tuple[str, ...]:
        keys: list[str] = []
        for path in self._root.rglob("*"):
            if not path.is_file() or path.name.endswith(".meta"):
                continue
            key = str(path.relative_to(self._root)).replace("\\", "/")
            if prefix and not key.startswith(prefix):
                continue
            keys.append(key)
        keys.sort()
        return tuple(keys)

    def _resolve_path(self, key: str) -> Path:
        normalized = key.strip().lstrip("/").replace("..", "")
        return self._root / normalized


class _CloudObjectStorageAdapter(BaseInfrastructureAdapter):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        client: ObjectStorageClient | None,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("object-storage", "cloud"),
                configuration_profile="default",
                compatibility=("object-storage:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError(f"{self.adapter_metadata.provider} storage client is required.")
        await super().start()

    async def put_object(self, key: str, payload: bytes, *, content_type: str | None = None) -> str:
        if self._client is None:
            raise RuntimeError("Object storage client is not configured.")
        return await self._client.put_object(key, payload, content_type=content_type)

    async def get_object(self, key: str) -> bytes:
        if self._client is None:
            raise RuntimeError("Object storage client is not configured.")
        return await self._client.get_object(key)

    async def delete_object(self, key: str) -> None:
        if self._client is None:
            raise RuntimeError("Object storage client is not configured.")
        await self._client.delete_object(key)

    async def list_objects(self, prefix: str = "") -> tuple[str, ...]:
        if self._client is None:
            raise RuntimeError("Object storage client is not configured.")
        return await self._client.list_objects(prefix=prefix)


class S3CompatibleStorageAdapter(_CloudObjectStorageAdapter):
    def __init__(self, *, client: ObjectStorageClient | None = None) -> None:
        super().__init__(
            identifier="storage.s3",
            provider="s3",
            client=client,
        )


class AzureBlobStorageAdapter(_CloudObjectStorageAdapter):
    def __init__(self, *, client: ObjectStorageClient | None = None) -> None:
        super().__init__(
            identifier="storage.azure_blob",
            provider="azure-blob",
            client=client,
        )


class GcsStorageAdapter(_CloudObjectStorageAdapter):
    def __init__(self, *, client: ObjectStorageClient | None = None) -> None:
        super().__init__(
            identifier="storage.gcs",
            provider="gcs",
            client=client,
        )


def build_object_keys(prefix: str, names: Iterable[str]) -> tuple[str, ...]:
    normalized_prefix = prefix.strip("/")
    keys = [f"{normalized_prefix}/{name.strip('/')}" for name in names]
    return tuple(key.strip("/") for key in keys)
