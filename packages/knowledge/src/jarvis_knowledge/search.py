from __future__ import annotations

from typing import Protocol

from jarvis_knowledge.models import (
    KnowledgeDocument,
    KnowledgeSearchQuery,
    ScoredKnowledge,
)
from jarvis_knowledge.engines import DefaultKnowledgeSearchEngine, DefaultKnowledgeRankingEngine


class EnhancedSearchEngine(Protocol):
    def search(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[KnowledgeDocument, ...]: ...
    def search_ranked(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[ScoredKnowledge, ...]: ...


class HybridSearchEngine:
    def __init__(self) -> None:
        self._search = DefaultKnowledgeSearchEngine()
        self._ranking = DefaultKnowledgeRankingEngine()
        from jarvis_knowledge.models import KnowledgeRankingContext
        from datetime import UTC, datetime

    def search(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[KnowledgeDocument, ...]:
        return self._search.search(documents, query)

    def search_ranked(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[ScoredKnowledge, ...]:
        matches = self._search.search(documents, query)
        if not matches:
            return ()
        from jarvis_knowledge.models import KnowledgeRankingContext
        context = KnowledgeRankingContext(
            requester_id="",
            workspace=query.workspace or "",
            project=query.project or "",
            query_terms=query.terms,
        )
        return self._ranking.rank(matches, context)


class FuzzySearchEngine:
    def __init__(self, threshold: float = 0.6) -> None:
        self._threshold = threshold

    def search(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[KnowledgeDocument, ...]:
        if not query.terms:
            return documents
        scored: list[tuple[float, KnowledgeDocument]] = []
        for doc in documents:
            score = self._fuzzy_match(doc, query.terms)
            if score >= self._threshold:
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return tuple(doc for _, doc in scored[:max(query.limit, 0) or len(scored)])

    def search_ranked(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[ScoredKnowledge, ...]:
        if not query.terms:
            return ()
        scored: list[tuple[float, KnowledgeDocument]] = []
        for doc in documents:
            score = self._fuzzy_match(doc, query.terms)
            if score >= self._threshold:
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return tuple(
            ScoredKnowledge(
                document=doc,
                score=round(score, 6),
                confidence=doc.metadata.confidence,
                reasons=("fuzzy_match",),
            )
            for score, doc in scored[:max(query.limit, 0) or len(scored)]
        )

    def _fuzzy_match(self, doc: KnowledgeDocument, terms: tuple[str, ...]) -> float:
        import re
        text = " ".join((
            doc.metadata.title,
            doc.metadata.description,
            doc.summary,
            " ".join(doc.metadata.tags),
        )).lower()
        words = set(re.findall(r"[a-zA-Z0-9_]+", text))
        hits = 0
        for term in terms:
            t = term.lower()
            if t in words:
                hits += 1
            else:
                for word in words:
                    if len(t) > 3 and len(word) > 3:
                        if t in word or word in t:
                            hits += 0.5
                            break
        return hits / len(terms) if terms else 0.0
