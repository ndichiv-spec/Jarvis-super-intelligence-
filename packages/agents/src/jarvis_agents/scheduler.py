from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ScheduledTask:
    task_id: str
    name: str
    interval_seconds: float
    action: str
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class InMemoryAgentScheduler:
    _scheduled_tasks: dict[str, ScheduledTask] = field(default_factory=dict)
    _handlers: dict[str, Callable[[], None]] = field(default_factory=dict)

    def schedule(
        self,
        name: str,
        interval_seconds: float,
        action: str,
        handler: Callable[[], None],
    ) -> ScheduledTask:
        task_id = f"sched-{uuid4().hex[:8]}"
        now = datetime.now(UTC)
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            interval_seconds=interval_seconds,
            action=action,
            next_run=now + timedelta(seconds=interval_seconds),
        )
        self._scheduled_tasks[task_id] = task
        self._handlers[task_id] = handler
        return task

    def cancel(self, task_id: str) -> bool:
        if task_id not in self._scheduled_tasks:
            return False
        self._scheduled_tasks.pop(task_id, None)
        self._handlers.pop(task_id, None)
        return True

    def pause(self, task_id: str) -> bool:
        task = self._scheduled_tasks.get(task_id)
        if task is None:
            return False
        updated = ScheduledTask(
            task_id=task.task_id,
            name=task.name,
            interval_seconds=task.interval_seconds,
            action=task.action,
            enabled=False,
            last_run=task.last_run,
            next_run=task.next_run,
            created_at=task.created_at,
        )
        self._scheduled_tasks[task_id] = updated
        return True

    def resume(self, task_id: str) -> bool:
        task = self._scheduled_tasks.get(task_id)
        if task is None:
            return False
        updated = ScheduledTask(
            task_id=task.task_id,
            name=task.name,
            interval_seconds=task.interval_seconds,
            action=task.action,
            enabled=True,
            next_run=datetime.now(UTC) + timedelta(seconds=task.interval_seconds),
            last_run=task.last_run,
            created_at=task.created_at,
        )
        self._scheduled_tasks[task_id] = updated
        return True

    def tick(self) -> tuple[str, ...]:
        now = datetime.now(UTC)
        executed: list[str] = []
        for task_id, task in list(self._scheduled_tasks.items()):
            if not task.enabled:
                continue
            if task.next_run is not None and now >= task.next_run:
                handler = self._handlers.get(task_id)
                if handler is not None:
                    handler()
                updated = ScheduledTask(
                    task_id=task.task_id,
                    name=task.name,
                    interval_seconds=task.interval_seconds,
                    action=task.action,
                    enabled=task.enabled,
                    last_run=now,
                    next_run=now + timedelta(seconds=task.interval_seconds),
                    created_at=task.created_at,
                )
                self._scheduled_tasks[task_id] = updated
                executed.append(task_id)
        return tuple(executed)

    def list_tasks(self) -> tuple[ScheduledTask, ...]:
        return tuple(self._scheduled_tasks.values())

    def get_task(self, task_id: str) -> ScheduledTask | None:
        return self._scheduled_tasks.get(task_id)

    def clear(self) -> None:
        self._scheduled_tasks.clear()
        self._handlers.clear()
