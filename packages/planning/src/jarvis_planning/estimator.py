from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Complexity(Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


COMPLEXITY_WEIGHTS: dict[Complexity, float] = {
    Complexity.TRIVIAL: 1.0,
    Complexity.SIMPLE: 2.0,
    Complexity.MODERATE: 5.0,
    Complexity.COMPLEX: 13.0,
    Complexity.VERY_COMPLEX: 34.0,
}

ESTIMATED_DURATIONS: dict[Complexity, str] = {
    Complexity.TRIVIAL: "minutes",
    Complexity.SIMPLE: "hours",
    Complexity.MODERATE: "days",
    Complexity.COMPLEX: "weeks",
    Complexity.VERY_COMPLEX: "months",
}


@dataclass
class Estimate:
    complexity: Complexity
    effort_hours: float
    duration_text: str
    confidence: float
    risk_level: str
    factors: list[str] = field(default_factory=list)
    breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "complexity": self.complexity.value,
            "effort_hours": self.effort_hours,
            "duration_text": self.duration_text,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "factors": self.factors,
            "breakdown": self.breakdown,
        }


class Estimator:
    def estimate(self, objective: str, domain: str = "", known_factors: list[str] | None = None) -> Estimate:
        factors = known_factors or []
        score = self._score_objective(objective, domain, factors)
        complexity = self._score_to_complexity(score)
        effort = COMPLEXITY_WEIGHTS[complexity]
        duration = ESTIMATED_DURATIONS[complexity]
        confidence = self._calculate_confidence(score, len(factors))
        risk = self._assess_risk(complexity, confidence)
        return Estimate(
            complexity=complexity,
            effort_hours=effort,
            duration_text=duration,
            confidence=confidence,
            risk_level=risk,
            factors=factors,
            breakdown={"objective_analysis": score},
        )

    def _score_objective(self, objective: str, domain: str, factors: list[str]) -> float:
        score = 1.0
        words = objective.lower().split()
        word_count = len(words)

        if word_count > 50:
            score += 3.0
        elif word_count > 20:
            score += 1.5
        elif word_count > 10:
            score += 0.5

        indicators = {
            "complex": 2.0, "integrate": 2.0, "platform": 1.5,
            "distributed": 2.0, "enterprise": 1.5, "cross-platform": 2.0,
            "microservice": 2.0, "real-time": 1.5, "multi-user": 1.5,
            "scale": 2.0, "secure": 1.5, "comprehensive": 1.0,
            "full-stack": 1.5, "mobile": 1.0, "web": 0.5,
            "api": 0.5, "database": 1.0, "authentication": 1.0,
            "payment": 1.5, "analytics": 1.5, "reporting": 1.0,
            "workflow": 1.5, "automation": 1.5, "ai": 2.0,
            "machine-learning": 2.5, "deep-learning": 3.0,
        }
        for word in set(words):
            score += indicators.get(word, 0.0)

        if domain:
            domain_bonus = {"finance": 1.0, "healthcare": 2.0, "aerospace": 2.5, "iot": 1.5, "blockchain": 2.0}
            score += domain_bonus.get(domain.lower(), 0.5)

        return score

    def _score_to_complexity(self, score: float) -> Complexity:
        if score <= 1.5:
            return Complexity.TRIVIAL
        if score <= 3.0:
            return Complexity.SIMPLE
        if score <= 6.0:
            return Complexity.MODERATE
        if score <= 12.0:
            return Complexity.COMPLEX
        return Complexity.VERY_COMPLEX

    def _calculate_confidence(self, score: float, factor_count: int) -> float:
        base = 0.7
        factor_bonus = min(factor_count * 0.05, 0.25)
        complexity_penalty = max(0.0, (score - 5.0) * 0.02)
        return min(max(base + factor_bonus - complexity_penalty, 0.1), 0.95)

    def _assess_risk(self, complexity: Complexity, confidence: float) -> str:
        if complexity in (Complexity.VERY_COMPLEX, Complexity.COMPLEX) and confidence < 0.5:
            return "high"
        if complexity == Complexity.VERY_COMPLEX:
            return "high"
        if complexity == Complexity.COMPLEX:
            return "medium"
        if confidence < 0.4:
            return "medium"
        return "low"

    @staticmethod
    def weighted_average(estimates: list[Estimate]) -> Estimate:
        if not estimates:
            return Estimate(Complexity.TRIVIAL, 0.0, "unknown", 1.0, "low")
        total_hours = sum(e.effort_hours * e.confidence for e in estimates)
        total_weight = sum(e.confidence for e in estimates)
        avg_hours = total_hours / total_weight if total_weight > 0 else 0.0
        avg_confidence = total_weight / len(estimates)
        max_complexity = max(estimates, key=lambda e: COMPLEXITY_WEIGHTS[e.complexity]).complexity
        risks = [e.risk_level for e in estimates]
        final_risk = "high" if "high" in risks else ("medium" if "medium" in risks else "low")
        return Estimate(
            complexity=max_complexity,
            effort_hours=round(avg_hours, 1),
            duration_text=ESTIMATED_DURATIONS.get(max_complexity, "unknown"),
            confidence=round(avg_confidence, 2),
            risk_level=final_risk,
        )
