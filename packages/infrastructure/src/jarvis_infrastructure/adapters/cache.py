from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.configuration import AdapterConfiguration
from jarvis_infrastructure.metadata import AdapterMetadata


class RedisClient(Protocol):
    async def get(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None: ...

    async def delete(self, key: str) -> None: ...

    async def ping(self) -> bool: ...


class InMemoryCacheAdapter(BaseInfrastructureAdapter):
    def __init__(self) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="cache.in_memory",
                version="1.0.0",
                provider="in-memory",
                capabilities=("cache", "ttl"),
                configuration_profile="default",
                compatibility=("cache:v1",),
            )
        )
        self._cache: dict[str, tuple[str, datetime | None]] = {}

    async def get(self, key: str) -> str | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if expiry is not None and expiry <= datetime.now(tz=UTC):
            self._cache.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        expiry = None
        if ttl_seconds is not None:
            expiry = datetime.now(tz=UTC) + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry)

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    async def clear(self) -> None:
        self._cache.clear()

    async def stats(self) -> Mapping[str, int]:
        return {"entries": len(self._cache)}


class RedisCacheAdapter(BaseInfrastructureAdapter):
    def __init__(self, *, client: RedisClient | None = None, namespace: str = "jarvis") -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="cache.redis",
                version="1.0.0",
                provider="redis",
                capabilities=("cache", "ttl", "distributed"),
                configuration_profile="default",
                compatibility=("cache:v1",),
            )
        )
        self._client = client
        self._namespace = namespace

    async def configure(self, configuration: AdapterConfiguration) -> None:
        await super().configure(configuration)
        namespace = configuration.settings.get("namespace")
        if namespace:
            self._namespace = namespace

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError("Redis client is required to start RedisCacheAdapter.")
        await super().start()

    async def get(self, key: str) -> str | None:
        if self._client is None:
            return None
        return await self._client.get(self._qualify(key))

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        if self._client is None:
            raise RuntimeError("Redis client is not configured.")
        await self._client.set(self._qualify(key), value, ttl_seconds=ttl_seconds)

    async def delete(self, key: str) -> None:
        if self._client is None:
            return
        await self._client.delete(self._qualify(key))

    async def clear(self) -> None:
        raise RuntimeError("Bulk cache clear is intentionally unsupported for Redis adapters.")

    async def ping(self) -> bool:
        if self._client is None:
            return False
        return await self._client.ping()

    def _qualify(self, key: str) -> str:
        return f"{self._namespace}:{key}"
