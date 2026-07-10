from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jarvis_intelligence.goals import Goal, GoalManager, GoalState, GoalPriority
from jarvis_intelligence.objectives import Objective
from jarvis_intelligence.tasks import Task, TaskGraph, TaskState
from jarvis_intelligence.strategies import Strategy, StrategySelector, StrategyType


@dataclass
class IntelligencePlan:
    id: str
    goal: Goal
    objectives: list[Objective] = field(default_factory=list)
    task_graph: TaskGraph = field(default_factory=TaskGraph)
    strategy: Strategy | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = "draft"

    @classmethod
    def create(cls, goal: Goal) -> IntelligencePlan:
        return cls(id=f"plan-{uuid4().hex[:12]}", goal=goal)


class IntelligencePlanner:
    def __init__(self, goal_manager: GoalManager | None = None) -> None:
        self._goal_manager = goal_manager or GoalManager()
        self._plans: dict[str, IntelligencePlan] = {}
        self._strategy_selector = StrategySelector()

    def create_plan(self, goal_description: str, priority: GoalPriority = GoalPriority.MEDIUM, capabilities: tuple[str, ...] | None = None) -> IntelligencePlan:
        goal = Goal.create(description=goal_description, priority=priority, required_capabilities=capabilities or ())
        self._goal_manager.add(goal)

        plan = IntelligencePlan.create(goal)
        strategy = self._strategy_selector.select(goal_description, "moderate", goal.required_capabilities)
        plan.strategy = strategy

        self._plans[plan.id] = plan
        return plan

    def add_objective(self, plan_id: str, description: str) -> Objective | None:
        plan = self._plans.get(plan_id)
        if plan is None:
            return None
        objective = Objective.create(description=description, goal_id=plan.goal.id)
        plan.objectives.append(objective)
        return objective

    def add_task(self, plan_id: str, description: str, depends_on: tuple[str, ...] | None = None, required_capabilities: tuple[str, ...] | None = None) -> Task | None:
        plan = self._plans.get(plan_id)
        if plan is None:
            return None
        task = Task.create(
            description=description,
            depends_on=depends_on,
            required_capabilities=required_capabilities,
        )
        plan.task_graph.add(task)
        return task

    def decompose_goal(self, plan_id: str) -> IntelligencePlan | None:
        plan = self._plans.get(plan_id)
        if plan is None:
            return None
        goal = plan.goal
        description = goal.description.lower()

        design_task = self.add_task(plan_id, f"Design {description} architecture", required_capabilities=("planning", "analysis"))
        if design_task is not None:
            build_task = self.add_task(plan_id, f"Build {description} components", depends_on=(design_task.id,), required_capabilities=("programming", "engineering"))
            if build_task is not None:
                test_task = self.add_task(plan_id, f"Test {description} thoroughly", depends_on=(build_task.id,), required_capabilities=("testing", "quality_assurance"))
                if test_task is not None:
                    doc_task = self.add_task(plan_id, f"Document {description}", depends_on=(build_task.id,), required_capabilities=("documentation",))
                    deploy_task = self.add_task(plan_id, f"Deploy {description}", depends_on=(test_task.id, doc_task.id), required_capabilities=("devops", "deployment"))
                    plan.status = "decomposed"

        plan.task_graph.get_ready_tasks()
        return plan

    def get_plan(self, plan_id: str) -> IntelligencePlan | None:
        return self._plans.get(plan_id)

    def list_plans(self) -> list[IntelligencePlan]:
        return list(self._plans.values())

    def get_goal_manager(self) -> GoalManager:
        return self._goal_manager
