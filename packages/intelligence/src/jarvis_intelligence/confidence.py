from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConfidenceScore:
    overall: float
    reasoning_quality: float = 0.0
    agent_capability: float = 0.0
    historical_success: float = 0.0
    data_completeness: float = 0.0
    risk_assessment: float = 0.0
    factors: dict[str, float] = field(default_factory=dict)


class ConfidenceEngine:
    def __init__(self) -> None:
        self._scores: dict[str, ConfidenceScore] = {}

    def compute(
        self,
        *,
        reasoning_quality: float = 0.7,
        agent_capability: float = 0.7,
        historical_success: float = 0.5,
        data_completeness: float = 0.8,
        risk_assessment: float = 0.6,
        weights: dict[str, float] | None = None,
    ) -> ConfidenceScore:
        w = weights or {
            "reasoning_quality": 0.30,
            "agent_capability": 0.25,
            "historical_success": 0.20,
            "data_completeness": 0.15,
            "risk_assessment": 0.10,
        }

        overall = (
            reasoning_quality * w.get("reasoning_quality", 0.30) +
            agent_capability * w.get("agent_capability", 0.25) +
            historical_success * w.get("historical_success", 0.20) +
            data_completeness * w.get("data_completeness", 0.15) +
            risk_assessment * w.get("risk_assessment", 0.10)
        )

        score = ConfidenceScore(
            overall=round(overall, 4),
            reasoning_quality=reasoning_quality,
            agent_capability=agent_capability,
            historical_success=historical_success,
            data_completeness=data_completeness,
            risk_assessment=risk_assessment,
            factors=dict(w),
        )

        score_id = f"conf-{id(score)}"
        self._scores[score_id] = score
        return score

    def classify(self, score: ConfidenceScore) -> str:
        if score.overall >= 0.8:
            return "high"
        if score.overall >= 0.5:
            return "medium"
        return "low"

    def should_proceed(self, score: ConfidenceScore, threshold: float = 0.5) -> bool:
        return score.overall >= threshold
