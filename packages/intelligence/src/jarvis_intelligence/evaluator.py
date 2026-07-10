from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_intelligence.tasks import TaskState


@dataclass
class EvaluationResult:
    task_id: str
    success: bool
    confidence: float
    quality_score: float
    efficiency_score: float
    error: str | None = None
    suggestions: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)


class EvaluationEngine:
    def __init__(self) -> None:
        self._results: dict[str, EvaluationResult] = {}

    def evaluate(self, task_description: str, result: dict[str, Any] | None = None, state: TaskState = TaskState.COMPLETED) -> EvaluationResult:
        task_id = f"eval-{datetime.now(UTC).timestamp()}"

        success = state == TaskState.COMPLETED
        quality = self._assess_quality(result, success)
        efficiency = self._assess_efficiency(result)
        confidence = (quality + efficiency) / 2

        eval_result = EvaluationResult(
            task_id=task_id,
            success=success,
            confidence=confidence,
            quality_score=quality,
            efficiency_score=efficiency,
            suggestions=self._generate_suggestions(result, quality, efficiency),
            metrics={
                "quality": quality,
                "efficiency": efficiency,
                "overall_confidence": confidence,
            },
        )

        self._results[task_id] = eval_result
        return eval_result

    def _assess_quality(self, result: dict[str, Any] | None, success: bool) -> float:
        if not success:
            return 0.0
        if result is None:
            return 0.7
        score = 1.0
        if "errors" in result and result["errors"]:
            score -= 0.3 * min(len(result["errors"]), 3)
        if "warnings" in result and result["warnings"]:
            score -= 0.1 * min(len(result["warnings"]), 5)
        return max(0.1, score)

    def _assess_efficiency(self, result: dict[str, Any] | None) -> float:
        if result is None:
            return 0.7
        duration = result.get("duration_seconds", 0)
        if duration < 1:
            return 1.0
        if duration < 5:
            return 0.9
        if duration < 30:
            return 0.7
        return 0.5

    def _generate_suggestions(self, result: dict[str, Any] | None, quality: float, efficiency: float) -> list[str]:
        suggestions: list[str] = []
        if quality < 0.6:
            suggestions.append("Improve quality checks and validation")
        if efficiency < 0.6:
            suggestions.append("Optimize execution time and resource usage")
        if result and result.get("errors"):
            suggestions.append("Address recurring errors in dependency chain")
        return suggestions

    def get_results(self) -> list[EvaluationResult]:
        return list(self._results.values())
