from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from jarvis_knowledge.models import (
    KnowledgeDocument,
    KnowledgeRankingContext,
    ScoredKnowledge,
)
from jarvis_knowledge.engines import DefaultKnowledgeRankingEngine


class EnhancedRankingEngine(Protocol):
    def rank(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]: ...
    def rank_with_boosts(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
        *,
        boosts: dict[str, float] | None = None,
    ) -> tuple[ScoredKnowledge, ...]: ...


class BoostedRankingEngine:
    def __init__(self) -> None:
        self._base = DefaultKnowledgeRankingEngine()

    def rank(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]:
        return self._base.rank(documents, context)

    def rank_with_boosts(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
        *,
        boosts: dict[str, float] | None = None,
    ) -> tuple[ScoredKnowledge, ...]:
        scored = self._base.rank(documents, context)
        if not boosts:
            return scored
        boosted: list[ScoredKnowledge] = []
        boost_keywords = {k.lower(): v for k, v in boosts.items()}
        for item in scored:
            text = f"{item.document.metadata.title} {item.document.summary}".lower()
            boost_factor = 1.0
            for keyword, factor in boost_keywords.items():
                if keyword in text:
                    boost_factor *= factor
            boosted.append(
                ScoredKnowledge(
                    document=item.document,
                    score=round(item.score * boost_factor, 6),
                    confidence=item.confidence,
                    reasons=(*item.reasons, "boosted"),
                )
            )
        boosted.sort(key=lambda x: -x.score)
        return tuple(boosted)


class RecencyWeightedRankingEngine:
    def __init__(self, half_life_days: float = 90.0) -> None:
        self._base = DefaultKnowledgeRankingEngine()
        self._half_life_days = half_life_days

    def rank(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]:
        return self._base.rank(documents, context)

    def rank_with_boosts(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
        *,
        boosts: dict[str, float] | None = None,
    ) -> tuple[ScoredKnowledge, ...]:
        import math
        scored = self._base.rank(documents, context)
        boosted: list[ScoredKnowledge] = []
        for item in scored:
            age_days = (context.now - item.document.metadata.updated_at).days
            recency_factor = 2.0 ** (-age_days / self._half_life_days)
            new_score = round(item.score * recency_factor, 6)
            boosted.append(
                ScoredKnowledge(
                    document=item.document,
                    score=new_score,
                    confidence=item.confidence,
                    reasons=(*item.reasons, "recency_weighted"),
                )
            )
        boosted.sort(key=lambda x: -x.score)
        return tuple(boosted)
