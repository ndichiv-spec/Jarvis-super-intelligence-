from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_agents.models import AgentGoal, GoalStatus


@dataclass(slots=True)
class InMemoryGoalManager:
    _goals: dict[str, AgentGoal] = field(default_factory=dict)

    def create_goal(self, goal: AgentGoal) -> AgentGoal:
        goal_id = goal.goal_id or f"goal-{uuid4().hex[:8]}"
        stored = AgentGoal(
            goal_id=goal_id,
            description=goal.description,
            priority=goal.priority,
            status=GoalStatus.ACTIVE,
            dependencies=goal.dependencies,
        )
        self._goals[stored.goal_id] = stored
        return stored

    def update_progress(self, goal_id: str, progress: float) -> AgentGoal:
        goal = self._goals.get(goal_id)
        if goal is None:
            msg = f"Goal not found: {goal_id}"
            raise KeyError(msg)
        updated = goal.with_progress(progress)
        self._goals[goal_id] = updated
        return updated

    def update_status(self, goal_id: str, status: str) -> AgentGoal:
        goal = self._goals.get(goal_id)
        if goal is None:
            msg = f"Goal not found: {goal_id}"
            raise KeyError(msg)
        updated = goal.with_status(GoalStatus(status))
        self._goals[goal_id] = updated
        return updated

    def get_goal(self, goal_id: str) -> AgentGoal | None:
        return self._goals.get(goal_id)

    def list_goals(self) -> tuple[AgentGoal, ...]:
        return tuple(self._goals.values())

    def list_goals_by_status(self, status: str) -> tuple[AgentGoal, ...]:
        return tuple(g for g in self._goals.values() if g.status.value == status)
