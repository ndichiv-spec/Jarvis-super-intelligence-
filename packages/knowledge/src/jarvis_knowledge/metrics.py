from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class MetricSample:
    name: str
    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KnowledgeMetrics:
    total_documents: int = 0
    total_chunks: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    total_sources: int = 0
    total_collections: int = 0
    avg_confidence: float = 0.0
    avg_completeness: float = 0.0
    total_searches: int = 0
    total_citations: int = 0
    last_updated: datetime | None = None
    custom: dict[str, float] = field(default_factory=dict)


class MetricsCollector(Protocol):
    def record(self, name: str, value: float, **labels: str) -> None: ...
    def snapshot(self) -> KnowledgeMetrics: ...
    def samples(self, name: str) -> tuple[MetricSample, ...]: ...


class InMemoryMetricsCollector:
    def __init__(self) -> None:
        self._samples: dict[str, list[MetricSample]] = {}

    def record(self, name: str, value: float, **labels: str) -> None:
        sample = MetricSample(
            name=name,
            value=value,
            timestamp=datetime.now(UTC),
            labels=dict(labels),
        )
        if name not in self._samples:
            self._samples[name] = []
        self._samples[name].append(sample)

    def snapshot(self) -> KnowledgeMetrics:
        doc_count = self._sum_metric("document.count")
        chunk_count = self._sum_metric("chunk.count")
        entity_count = self._sum_metric("entity.count")
        rel_count = self._sum_metric("relationship.count")
        source_count = self._sum_metric("source.count")
        col_count = self._sum_metric("collection.count")
        search_count = self._sum_metric("search.count")
        citation_count = self._sum_metric("citation.count")
        avg_conf = self._avg_metric("document.confidence")
        avg_comp = self._avg_metric("document.completeness")
        return KnowledgeMetrics(
            total_documents=int(doc_count),
            total_chunks=int(chunk_count),
            total_entities=int(entity_count),
            total_relationships=int(rel_count),
            total_sources=int(source_count),
            total_collections=int(col_count),
            avg_confidence=avg_conf,
            avg_completeness=avg_comp,
            total_searches=int(search_count),
            total_citations=int(citation_count),
            last_updated=datetime.now(UTC),
        )

    def samples(self, name: str) -> tuple[MetricSample, ...]:
        return tuple(self._samples.get(name, []))

    def _sum_metric(self, name: str) -> float:
        samples = self._samples.get(name, [])
        return sum(s.value for s in samples)

    def _avg_metric(self, name: str) -> float:
        samples = self._samples.get(name, [])
        if not samples:
            return 0.0
        return sum(s.value for s in samples) / len(samples)

    def clear(self) -> None:
        self._samples.clear()
