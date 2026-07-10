from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import sqrt
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


@dataclass(frozen=True, slots=True)
class VectorRecord:
    identifier: str
    vector: tuple[float, ...]
    metadata: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    identifier: str
    score: float
    metadata: Mapping[str, str]


class VectorStoreClient(Protocol):
    async def upsert(self, records: tuple[VectorRecord, ...]) -> None: ...

    async def search(
        self, query_vector: tuple[float, ...], limit: int
    ) -> tuple[VectorSearchResult, ...]: ...


class InMemoryVectorStoreAdapter(BaseInfrastructureAdapter):
    def __init__(self) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="vector.in_memory",
                version="1.0.0",
                provider="in-memory",
                capabilities=("vector-store", "semantic-search"),
                configuration_profile="default",
                compatibility=("vector-store:v1",),
            )
        )
        self._records: dict[str, VectorRecord] = {}

    async def upsert(self, records: tuple[VectorRecord, ...]) -> None:
        for record in records:
            self._records[record.identifier] = record

    async def search(
        self, query_vector: tuple[float, ...], limit: int = 5
    ) -> tuple[VectorSearchResult, ...]:
        scored: list[VectorSearchResult] = []
        for record in self._records.values():
            score = _cosine_similarity(query_vector, record.vector)
            scored.append(
                VectorSearchResult(
                    identifier=record.identifier,
                    score=score,
                    metadata=record.metadata,
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return tuple(scored[:limit])


class _ExternalVectorStoreAdapter(BaseInfrastructureAdapter):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        client: VectorStoreClient | None,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("vector-store", "semantic-search", "distributed"),
                configuration_profile="default",
                compatibility=("vector-store:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError(f"{self.adapter_metadata.provider} client is required.")
        await super().start()

    async def upsert(self, records: tuple[VectorRecord, ...]) -> None:
        if self._client is None:
            raise RuntimeError("Vector store client is not configured.")
        await self._client.upsert(records)

    async def search(
        self, query_vector: tuple[float, ...], limit: int = 5
    ) -> tuple[VectorSearchResult, ...]:
        if self._client is None:
            raise RuntimeError("Vector store client is not configured.")
        return await self._client.search(query_vector, limit)


class QdrantVectorStoreAdapter(_ExternalVectorStoreAdapter):
    def __init__(self, *, client: VectorStoreClient | None = None) -> None:
        super().__init__(
            identifier="vector.qdrant",
            provider="qdrant",
            client=client,
        )


class MilvusVectorStoreAdapter(_ExternalVectorStoreAdapter):
    def __init__(self, *, client: VectorStoreClient | None = None) -> None:
        super().__init__(
            identifier="vector.milvus",
            provider="milvus",
            client=client,
        )


class PgVectorStoreAdapter(_ExternalVectorStoreAdapter):
    def __init__(self, *, client: VectorStoreClient | None = None) -> None:
        super().__init__(
            identifier="vector.pgvector",
            provider="pgvector",
            client=client,
        )


def _cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)
