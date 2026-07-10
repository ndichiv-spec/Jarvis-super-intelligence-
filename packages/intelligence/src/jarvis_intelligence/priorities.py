from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_intelligence.goals import Goal, GoalPriority, GoalState


@dataclass
class PriorityAssessment:
    goal_id: str
    urgency_score: float
    importance_score: float
    overall_priority: float
    factors: dict[str, float] = field(default_factory=dict)


class PriorityEngine:
    def assess(self, goal: Goal) -> PriorityAssessment:
        urgency = self._assess_urgency(goal)
        importance = self._assess_importance(goal)
        overall = (urgency * 0.4 + importance * 0.6)

        return PriorityAssessment(
            goal_id=goal.id,
            urgency_score=urgency,
            importance_score=importance,
            overall_priority=round(overall, 4),
            factors={
                "priority_weight": self._priority_weight(goal.priority),
                "deadline_proximity": self._deadline_factor(goal),
                "dependency_count": len(goal.dependencies) * 0.05,
            },
        )

    def _assess_urgency(self, goal: Goal) -> float:
        score = 0.5
        if goal.deadline:
            remaining = goal.deadline - datetime.now(UTC)
            hours = remaining.total_seconds() / 3600
            if hours < 1:
                score += 0.4
            elif hours < 24:
                score += 0.3
            elif hours < 168:
                score += 0.1
        if goal.state == GoalState.IN_PROGRESS:
            score += 0.1
        return min(1.0, score)

    def _assess_importance(self, goal: Goal) -> float:
        return self._priority_weight(goal.priority)

    def _priority_weight(self, priority: GoalPriority) -> float:
        weights = {
            GoalPriority.LOWEST: 0.1,
            GoalPriority.LOW: 0.3,
            GoalPriority.MEDIUM: 0.5,
            GoalPriority.HIGH: 0.75,
            GoalPriority.CRITICAL: 1.0,
        }
        return weights.get(priority, 0.5)

    def _deadline_factor(self, goal: Goal) -> float:
        if goal.deadline is None:
            return 0.0
        remaining = goal.deadline - datetime.now(UTC)
        hours = remaining.total_seconds() / 3600
        if hours <= 0:
            return 1.0
        return max(0.0, 1.0 - (hours / 720))
