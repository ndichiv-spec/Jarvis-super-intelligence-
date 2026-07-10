from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class DecisionType(StrEnum):
    SELECT_STRATEGY = "select_strategy"
    ASSIGN_AGENT = "assign_agent"
    EXECUTE_TASK = "execute_task"
    RETRY_TASK = "retry_task"
    SKIP_TASK = "skip_task"
    REPLAN = "replan"
    ESCALATE = "escalate"
    COMPLETE_GOAL = "complete_goal"
    CANCEL_GOAL = "cancel_goal"


@dataclass(frozen=True, slots=True)
class Decision:
    type: DecisionType
    reasoning: str
    confidence: float
    target_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    alternatives: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class DecisionEngine:
    def __init__(self) -> None:
        self._history: list[Decision] = []

    def decide(
        self,
        decision_type: DecisionType,
        context: dict[str, Any],
        confidence_threshold: float = 0.5,
    ) -> Decision:
        method = getattr(self, f"_decide_{decision_type.value}", self._decide_default)
        decision = method(context, confidence_threshold)
        self._history.append(decision)
        return decision

    def _decide_select_strategy(self, context: dict[str, Any], threshold: float) -> Decision:
        complexity = context.get("complexity", "moderate")
        confidence = 0.85 if complexity != "complex" else 0.70
        return Decision(
            type=DecisionType.SELECT_STRATEGY,
            reasoning=f"Selected {'hierarchical' if complexity == 'complex' else 'sequential'} strategy based on complexity: {complexity}",
            confidence=confidence,
            target_id=context.get("goal_id"),
            parameters={"strategy": "hierarchical" if complexity == "complex" else "sequential"},
        )

    def _decide_assign_agent(self, context: dict[str, Any], threshold: float) -> Decision:
        required = context.get("required_capabilities", [])
        available = context.get("available_agents", [])
        confidence = 0.75 if available else 0.40
        return Decision(
            type=DecisionType.ASSIGN_AGENT,
            reasoning=f"Matching {required} against {len(available)} available agents",
            confidence=confidence,
            target_id=context.get("task_id"),
            parameters={"required_capabilities": required, "available_agents": len(available)},
            risks=("No matching agent found",) if not available else (),
        )

    def _decide_execute_task(self, context: dict[str, Any], threshold: float) -> Decision:
        task_ready = context.get("task_ready", False)
        confidence = 0.90 if task_ready else 0.30
        return Decision(
            type=DecisionType.EXECUTE_TASK,
            reasoning=f"Task {'ready' if task_ready else 'not ready'} for execution",
            confidence=confidence,
            target_id=context.get("task_id"),
            risks=("Task dependencies not met",) if not task_ready else (),
        )

    def _decide_retry_task(self, context: dict[str, Any], threshold: float) -> Decision:
        retry_count = context.get("retry_count", 0)
        max_retries = context.get("max_retries", 3)
        can_retry = retry_count < max_retries
        confidence = 0.60 if can_retry else 0.10
        return Decision(
            type=DecisionType.RETRY_TASK,
            reasoning=f"Retry attempt {retry_count + 1}/{max_retries}: {'possible' if can_retry else 'max reached'}",
            confidence=confidence,
            target_id=context.get("task_id"),
            parameters={"retry_count": retry_count, "max_retries": max_retries},
        )

    def _decide_replan(self, context: dict[str, Any], threshold: float) -> Decision:
        failures = context.get("failure_count", 0)
        confidence = 0.65 if failures > 0 else 0.20
        return Decision(
            type=DecisionType.REPLAN,
            reasoning=f"Replanning due to {failures} failures",
            confidence=confidence,
            target_id=context.get("plan_id"),
            parameters={"failure_count": failures},
        )

    def _decide_default(self, context: dict[str, Any], threshold: float) -> Decision:
        return Decision(
            type=DecisionType.EXECUTE_TASK,
            reasoning="Default decision",
            confidence=0.50,
        )

    def get_history(self) -> list[Decision]:
        return list(self._history)
