from __future__ import annotations

from typing import Protocol

from jarvis_knowledge.retrieval import RetrievalResult


class RerankingEngine(Protocol):
    def rerank(
        self,
        results: tuple[RetrievalResult, ...],
        query: str,
        *,
        top_k: int | None = None,
    ) -> tuple[RetrievalResult, ...]: ...


class PassThroughReranker:
    def rerank(
        self,
        results: tuple[RetrievalResult, ...],
        query: str,
        *,
        top_k: int | None = None,
    ) -> tuple[RetrievalResult, ...]:
        if top_k is not None and top_k < len(results):
            return results[:top_k]
        return results


class DiversityReranker:
    def __init__(self, similarity_threshold: float = 0.85) -> None:
        self._threshold = similarity_threshold

    def rerank(
        self,
        results: tuple[RetrievalResult, ...],
        query: str,
        *,
        top_k: int | None = None,
    ) -> tuple[RetrievalResult, ...]:
        if not results:
            return ()

        selected: list[RetrievalResult] = [results[0]]
        for result in results[1:]:
            if top_k is not None and len(selected) >= top_k:
                break
            if all(not self._overlap(result.entry.text, s.entry.text) for s in selected):
                selected.append(result)

        return tuple(selected)

    def _overlap(self, a: str, b: str) -> bool:
        a_words = set(a.lower().split())
        b_words = set(b.lower().split())
        if not a_words or not b_words:
            return False
        intersection = a_words & b_words
        union = a_words | b_words
        jaccard = len(intersection) / len(union)
        return jaccard > self._threshold
