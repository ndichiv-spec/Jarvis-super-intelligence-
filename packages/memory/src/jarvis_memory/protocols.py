from __future__ import annotations

from datetime import datetime
from typing import Protocol

from jarvis_memory.models import (
    ForgetDecision,
    MemoryPolicy,
    MemoryRecord,
    PolicyScope,
    RankingContext,
    RetrievalQuery,
    ScoredMemory,
    TimelineEvent,
)


class MemoryStore(Protocol):
    def put(self, memory: MemoryRecord) -> None: ...

    def get(self, identifier: str) -> MemoryRecord | None: ...

    def remove(self, identifier: str) -> None: ...

    def list(self) -> tuple[MemoryRecord, ...]: ...


class RetrievalEngine(Protocol):
    def search(
        self, memories: tuple[MemoryRecord, ...], query: RetrievalQuery
    ) -> tuple[MemoryRecord, ...]: ...


class RankingEngine(Protocol):
    def rank(
        self, memories: tuple[MemoryRecord, ...], context: RankingContext
    ) -> tuple[ScoredMemory, ...]: ...


class ConsolidationEngine(Protocol):
    def consolidate(self, memories: tuple[MemoryRecord, ...]) -> tuple[MemoryRecord, ...]: ...


class ForgettingEngine(Protocol):
    def evaluate(
        self, memory: MemoryRecord, policy: MemoryPolicy, now: datetime
    ) -> ForgetDecision: ...


class MemoryPolicyEngine(Protocol):
    def resolve(self, scope: PolicyScope) -> MemoryPolicy: ...


class TimelineEngine(Protocol):
    def build(self, memories: tuple[MemoryRecord, ...]) -> tuple[TimelineEvent, ...]: ...
