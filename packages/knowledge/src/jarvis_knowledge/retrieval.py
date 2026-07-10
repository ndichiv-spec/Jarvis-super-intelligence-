from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from jarvis_knowledge.embeddings import EmbeddingEngine, EmbeddingVector
from jarvis_knowledge.indexing import IndexEntry, SearchIndex


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    entry: IndexEntry
    score: float


class RetrievalEngine(Protocol):
    def retrieve(
        self,
        query_vector: EmbeddingVector,
        index: SearchIndex,
        *,
        top_k: int = 10,
    ) -> tuple[RetrievalResult, ...]: ...


class SimilarityRetrievalEngine:
    def __init__(self, embedding_engine: EmbeddingEngine) -> None:
        self._embedding_engine = embedding_engine

    def retrieve(
        self,
        query_vector: EmbeddingVector,
        index: SearchIndex,
        *,
        top_k: int = 10,
    ) -> tuple[RetrievalResult, ...]:
        scored: list[tuple[float, IndexEntry]] = []
        for entry in index.list_entries():
            sim = self._embedding_engine.similarity(query_vector, entry.embedding)
            scored.append((sim, entry))
        scored.sort(key=lambda x: -x[0])
        return tuple(
            RetrievalResult(entry=entry, score=score)
            for score, entry in scored[:top_k]
        )


class KeywordRetrievalEngine:
    def retrieve(
        self,
        query_vector: EmbeddingVector,
        index: SearchIndex,
        *,
        top_k: int = 10,
    ) -> tuple[RetrievalResult, ...]:
        import re
        _tokens = set(re.findall(r"[a-zA-Z0-9_]+", str(query_vector.values)[:200].lower()))
        scored: list[tuple[float, IndexEntry]] = []
        for entry in index.list_entries():
            text_lower = entry.text.lower()
            hits = sum(1 for t in _tokens if t in text_lower)
            score = hits / max(len(_tokens), 1)
            scored.append((score, entry))
        scored.sort(key=lambda x: -x[0])
        return tuple(
            RetrievalResult(entry=entry, score=score)
            for score, entry in scored[:top_k]
        )
