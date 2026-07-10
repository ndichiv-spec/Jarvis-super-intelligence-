from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jarvis_intelligence.tasks import Task, TaskState


@dataclass
class ScheduledTask:
    id: str
    task: Task
    scheduled_at: datetime
    interval_seconds: float | None = None
    last_run: datetime | None = None
    next_run: datetime | None = None
    is_recurring: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class SchedulerEngine:
    def __init__(self) -> None:
        self._scheduled: dict[str, ScheduledTask] = {}
        self._running: bool = False

    def schedule(self, task: Task, interval_seconds: float | None = None) -> ScheduledTask:
        now = datetime.now(UTC)
        st = ScheduledTask(
            id=f"sched-{uuid4().hex[:12]}",
            task=task,
            scheduled_at=now,
            interval_seconds=interval_seconds,
            is_recurring=interval_seconds is not None,
            next_run=now,
        )
        self._scheduled[st.id] = st
        return st

    def get_due(self) -> list[ScheduledTask]:
        now = datetime.now(UTC)
        return [st for st in self._scheduled.values() if st.next_run is not None and st.next_run <= now and st.task.state not in (TaskState.RUNNING, TaskState.COMPLETED)]

    def mark_completed(self, sched_id: str) -> None:
        st = self._scheduled.get(sched_id)
        if st is None:
            return
        now = datetime.now(UTC)
        updated = object.__new__(ScheduledTask)
        for key in ScheduledTask.__dataclass_fields__:
            setattr(updated, key, getattr(st, key))
        updated.last_run = now
        updated.next_run = now + timedelta(seconds=st.interval_seconds) if st.interval_seconds else None
        self._scheduled[sched_id] = updated

    def list_scheduled(self) -> list[ScheduledTask]:
        return list(self._scheduled.values())
