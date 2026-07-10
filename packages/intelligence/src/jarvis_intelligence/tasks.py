from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class TaskState(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    RETRYING = "retrying"


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    description: str
    objective_id: str | None = None
    goal_id: str | None = None
    state: TaskState = TaskState.PENDING
    parent_task_id: str | None = None
    child_task_ids: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    assigned_agent_id: str | None = None
    required_capabilities: tuple[str, ...] = ()
    priority: int = 50
    max_retries: int = 3
    retry_count: int = 0
    timeout_seconds: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        description: str,
        *,
        depends_on: tuple[str, ...] | None = None,
        required_capabilities: tuple[str, ...] | None = None,
        priority: int = 50,
        max_retries: int = 3,
        timeout_seconds: float | None = None,
    ) -> Task:
        return cls(
            id=f"task-{uuid4().hex[:12]}",
            description=description,
            depends_on=depends_on or (),
            required_capabilities=required_capabilities or (),
            priority=priority,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )


class TaskGraph:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def update(self, task_id: str, **updates: Any) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        frozen = task.__dataclass_fields__
        vals = {f: updates.get(f, getattr(task, f)) for f in frozen}
        updated = Task(**vals)
        self._tasks[task_id] = updated
        return updated

    def get_ready_tasks(self) -> list[Task]:
        ready: list[Task] = []
        for task in self._tasks.values():
            if task.state != TaskState.PENDING:
                continue
            deps_met = all(
                self._tasks.get(dep_id) is not None and self._tasks[dep_id].state == TaskState.COMPLETED
                for dep_id in task.depends_on
            )
            if deps_met:
                ready.append(task)
        return sorted(ready, key=lambda t: t.priority, reverse=True)

    def get_by_state(self, state: TaskState) -> list[Task]:
        return [t for t in self._tasks.values() if t.state == state]

    def all(self) -> list[Task]:
        return list(self._tasks.values())

    def topological_sort(self) -> list[Task]:
        visited: set[str] = set()
        result: list[Task] = []

        def visit(task_id: str) -> None:
            if task_id in visited:
                return
            visited.add(task_id)
            task = self._tasks.get(task_id)
            if task is None:
                return
            for dep_id in task.depends_on:
                visit(dep_id)
            result.append(task)

        for task_id in list(self._tasks.keys()):
            visit(task_id)
        return result
