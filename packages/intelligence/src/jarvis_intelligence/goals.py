from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4


class GoalState(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    ON_HOLD = "on_hold"


class GoalPriority(StrEnum):
    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class Goal:
    id: str
    description: str
    priority: GoalPriority
    state: GoalState = GoalState.DRAFT
    constraints: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    deadline: datetime | None = None
    required_capabilities: tuple[str, ...] = ()
    owner: str = "system"
    workspace_id: str = "default"
    parent_goal_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        description: str,
        priority: GoalPriority = GoalPriority.MEDIUM,
        *,
        constraints: tuple[str, ...] | None = None,
        success_criteria: tuple[str, ...] | None = None,
        dependencies: tuple[str, ...] | None = None,
        deadline: datetime | None = None,
        required_capabilities: tuple[str, ...] | None = None,
        owner: str = "system",
        workspace_id: str = "default",
        parent_goal_id: str | None = None,
    ) -> Goal:
        return cls(
            id=f"goal-{uuid4().hex[:12]}",
            description=description,
            priority=priority,
            constraints=constraints or (),
            success_criteria=success_criteria or (),
            dependencies=dependencies or (),
            deadline=deadline,
            required_capabilities=required_capabilities or (),
            owner=owner,
            workspace_id=workspace_id,
            parent_goal_id=parent_goal_id,
        )

    def is_overdue(self) -> bool:
        if self.deadline is None:
            return False
        return datetime.now(UTC) > self.deadline

    def remaining_time(self) -> timedelta | None:
        if self.deadline is None:
            return None
        return self.deadline - datetime.now(UTC)


class GoalManager:
    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}

    def add(self, goal: Goal) -> Goal:
        self._goals[goal.id] = goal
        return goal

    def get(self, goal_id: str) -> Goal | None:
        return self._goals.get(goal_id)

    def update(self, goal_id: str, **updates: Any) -> Goal | None:
        goal = self._goals.get(goal_id)
        if goal is None:
            return None
        frozen = goal.__dataclass_fields__
        vals = {f: updates.get(f, getattr(goal, f)) for f in frozen}
        vals["updated_at"] = datetime.now(UTC)
        updated = Goal(**vals)
        self._goals[goal_id] = updated
        return updated

    def list(self, state: GoalState | None = None) -> list[Goal]:
        goals = list(self._goals.values())
        if state is not None:
            goals = [g for g in goals if g.state == state]
        priority_order = {p.value: i for i, p in enumerate(GoalPriority)}
        return sorted(goals, key=lambda g: (priority_order.get(g.priority.value, 99), g.created_at), reverse=True)

    def remove(self, goal_id: str) -> bool:
        return self._goals.pop(goal_id, None) is not None

    def count(self) -> int:
        return len(self._goals)
