from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_intelligence.goals import Goal
from jarvis_intelligence.tasks import Task, TaskGraph


@dataclass
class SafetyCheck:
    passed: bool
    check_name: str
    details: str = ""
    severity: str = "info"


class SafetyEngine:
    def __init__(self) -> None:
        self._checks: list[SafetyCheck] = []

    def validate_goal(self, goal: Goal) -> list[SafetyCheck]:
        checks: list[SafetyCheck] = []

        if goal.deadline is None:
            checks.append(SafetyCheck(passed=True, check_name="no_deadline", details="No deadline set", severity="info"))

        if len(goal.description) > 2000:
            checks.append(SafetyCheck(passed=False, check_name="description_length", details="Goal description exceeds 2000 characters", severity="warning"))

        checks.append(SafetyCheck(passed=True, check_name="goal_valid", details="Goal structure is valid", severity="info"))
        self._checks.extend(checks)
        return checks

    def validate_task_graph(self, graph: TaskGraph) -> list[SafetyCheck]:
        checks: list[SafetyCheck] = []
        tasks = graph.all()

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            task = graph.get(task_id)
            if task:
                for dep_id in task.depends_on:
                    if dep_id not in visited:
                        if has_cycle(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True
            rec_stack.discard(task_id)
            return False

        for task in tasks:
            if task.id not in visited:
                if has_cycle(task.id):
                    checks.append(SafetyCheck(passed=False, check_name="circular_dependency", details=f"Circular dependency detected involving task {task.id}", severity="critical"))

        max_depth = 0
        for task in tasks:
            depth = 0
            current = task
            while current.parent_task_id:
                depth += 1
                parent = graph.get(current.parent_task_id)
                if parent is None:
                    break
                current = parent
            max_depth = max(max_depth, depth)

        if max_depth > 20:
            checks.append(SafetyCheck(passed=False, check_name="max_depth", details=f"Task graph depth {max_depth} exceeds limit of 20", severity="warning"))

        if not checks:
            checks.append(SafetyCheck(passed=True, check_name="task_graph_valid", details="Task graph is safe", severity="info"))

        self._checks.extend(checks)
        return checks

    def validate_execution(self, task: Task) -> list[SafetyCheck]:
        checks: list[SafetyCheck] = []

        if task.max_retries > 10:
            checks.append(SafetyCheck(passed=False, check_name="max_retries", details=f"max_retries={task.max_retries} exceeds safe limit of 10", severity="warning"))

        if task.timeout_seconds and task.timeout_seconds > 86400:
            checks.append(SafetyCheck(passed=False, check_name="timeout", details=f"timeout={task.timeout_seconds}s exceeds 24h limit", severity="warning"))

        checks.append(SafetyCheck(passed=True, check_name="execution_safe", details="Execution parameters are within safety limits", severity="info"))
        self._checks.extend(checks)
        return checks

    def get_all_checks(self) -> list[SafetyCheck]:
        return list(self._checks)
