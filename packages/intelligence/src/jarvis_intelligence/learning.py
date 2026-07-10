from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_intelligence.evaluator import EvaluationResult


@dataclass
class LearningRecord:
    id: str
    pattern: str
    context: str
    outcome: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)
    applied_count: int = 0


class LearningEngine:
    def __init__(self) -> None:
        self._records: list[LearningRecord] = []

    def record_success(self, goal_description: str, strategy_used: str, evaluation: EvaluationResult) -> LearningRecord:
        record = LearningRecord(
            id=f"learn-{datetime.now(UTC).timestamp()}",
            pattern=f"goal:{goal_description[:80]}",
            context=f"Strategy: {strategy_used}",
            outcome=f"Success (quality={evaluation.quality_score:.2f}, efficiency={evaluation.efficiency_score:.2f})",
            confidence=evaluation.confidence,
            metadata={"goal": goal_description, "strategy": strategy_used},
        )
        self._records.append(record)
        return record

    def record_failure(self, goal_description: str, strategy_used: str, error: str) -> LearningRecord:
        record = LearningRecord(
            id=f"learn-{datetime.now(UTC).timestamp()}",
            pattern=f"goal:{goal_description[:80]}",
            context=f"Strategy: {strategy_used}",
            outcome=f"Failure: {error}",
            confidence=0.3,
            metadata={"goal": goal_description, "strategy": strategy_used, "error": error},
        )
        self._records.append(record)
        return record

    def get_recommendation(self, goal_description: str) -> str | None:
        similar = [
            r for r in self._records
            if r.pattern.lower() in goal_description.lower() or goal_description.lower() in r.pattern.lower()
        ]
        if not similar:
            return None
        best = max(similar, key=lambda r: r.confidence * (r.applied_count + 1))
        return best.context

    def apply_record(self, record_id: str) -> None:
        for record in self._records:
            if record.id == record_id:
                object.__setattr__(record, "applied_count", record.applied_count + 1)
                break

    def get_all(self) -> list[LearningRecord]:
        return list(self._records)
