from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


@dataclass(frozen=True, slots=True)
class SearchDocument:
    identifier: str
    text: str
    metadata: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class SearchHit:
    identifier: str
    score: float
    metadata: Mapping[str, str]


class SearchClient(Protocol):
    async def index(self, document: SearchDocument) -> None: ...

    async def search(self, query: str, limit: int) -> tuple[SearchHit, ...]: ...


class InMemorySearchAdapter(BaseInfrastructureAdapter):
    def __init__(self) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="search.in_memory",
                version="1.0.0",
                provider="in-memory",
                capabilities=("search", "full-text"),
                configuration_profile="default",
                compatibility=("search:v1",),
            )
        )
        self._documents: dict[str, SearchDocument] = {}

    async def index(self, document: SearchDocument) -> None:
        self._documents[document.identifier] = document

    async def search(self, query: str, limit: int = 10) -> tuple[SearchHit, ...]:
        terms = [term for term in query.lower().split() if term]
        hits: list[SearchHit] = []
        for document in self._documents.values():
            score = _text_score(document.text, terms)
            if score <= 0:
                continue
            hits.append(
                SearchHit(
                    identifier=document.identifier,
                    score=score,
                    metadata=document.metadata,
                )
            )
        hits.sort(key=lambda item: item.score, reverse=True)
        return tuple(hits[:limit])


class _ExternalSearchAdapter(BaseInfrastructureAdapter):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        client: SearchClient | None,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("search", "full-text", "distributed"),
                configuration_profile="default",
                compatibility=("search:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError(f"{self.adapter_metadata.provider} client is required.")
        await super().start()

    async def index(self, document: SearchDocument) -> None:
        if self._client is None:
            raise RuntimeError("Search client is not configured.")
        await self._client.index(document)

    async def search(self, query: str, limit: int = 10) -> tuple[SearchHit, ...]:
        if self._client is None:
            raise RuntimeError("Search client is not configured.")
        return await self._client.search(query, limit)


class OpenSearchAdapter(_ExternalSearchAdapter):
    def __init__(self, *, client: SearchClient | None = None) -> None:
        super().__init__(
            identifier="search.opensearch",
            provider="opensearch",
            client=client,
        )


class ElasticsearchAdapter(_ExternalSearchAdapter):
    def __init__(self, *, client: SearchClient | None = None) -> None:
        super().__init__(
            identifier="search.elasticsearch",
            provider="elasticsearch",
            client=client,
        )


def _text_score(text: str, terms: list[str]) -> float:
    normalized = text.lower()
    score = 0.0
    for term in terms:
        if term in normalized:
            score += float(normalized.count(term))
    return score
