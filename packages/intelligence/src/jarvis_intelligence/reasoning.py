from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ReasoningMode(StrEnum):
    ANALYTICAL = "analytical"
    SEQUENTIAL = "sequential"
    STRATEGIC = "strategic"
    COMPARATIVE = "comparative"
    REFLECTIVE = "reflective"
    CONSTRAINT_BASED = "constraint_based"
    MULTI_STEP = "multi_step"


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    mode: ReasoningMode
    conclusion: str
    confidence: float
    steps: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningEngine:
    def __init__(self) -> None:
        self._history: list[ReasoningResult] = []

    def reason(self, context: str, mode: ReasoningMode = ReasoningMode.ANALYTICAL, constraints: tuple[str, ...] | None = None) -> ReasoningResult:
        method = getattr(self, f"_reason_{mode.value}", self._reason_analytical)
        result = method(context, constraints or ())
        self._history.append(result)
        return result

    def _reason_analytical(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.ANALYTICAL,
            conclusion=f"Analyzed: {context[:100]}...",
            confidence=0.85,
            steps=("identify_facts", "evaluate_patterns", "draw_conclusions"),
            assumptions=("Data is complete",),
            risks=("Missing edge cases",),
        )

    def _reason_sequential(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.SEQUENTIAL,
            conclusion=f"Sequential plan for: {context[:100]}...",
            confidence=0.80,
            steps=("step_1", "step_2", "step_3", "step_n"),
            assumptions=("Steps are independent",),
        )

    def _reason_strategic(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.STRATEGIC,
            conclusion=f"Strategic approach for: {context[:100]}...",
            confidence=0.75,
            steps=("assess_resources", "evaluate_options", "select_strategy"),
            alternatives=("Conservative path", "Aggressive path"),
            risks=("Resource constraints", "Timeline pressure"),
        )

    def _reason_comparative(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.COMPARATIVE,
            conclusion=f"Comparison result for: {context[:100]}...",
            confidence=0.70,
            steps=("identify_options", "evaluate_criteria", "rank"),
            alternatives=("Option A", "Option B"),
        )

    def _reason_reflective(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.REFLECTIVE,
            conclusion=f"Reflective analysis: {context[:100]}...",
            confidence=0.60,
            steps=("review_history", "identify_patterns", "extract_lessons"),
            assumptions=("History is relevant",),
        )

    def _reason_constraint_based(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.CONSTRAINT_BASED,
            conclusion=f"Constraint-satisfying solution for: {context[:100]}...",
            confidence=0.65,
            steps=("identify_constraints", "map_solutions", "validate"),
            assumptions=("Constraints are correct",),
        )

    def _reason_multi_step(self, context: str, constraints: tuple[str, ...]) -> ReasoningResult:
        return ReasoningResult(
            mode=ReasoningMode.MULTI_STEP,
            conclusion=f"Multi-step decomposition for: {context[:100]}...",
            confidence=0.72,
            steps=("decompose", "order", "execute_sequence"),
        )

    def get_history(self) -> list[ReasoningResult]:
        return list(self._history)
