from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_planning.events import Event, EventBus, EventType
from jarvis_planning.executor import Executor
from jarvis_planning.scheduler import Scheduler


@dataclass
class ProgressReport:
    plan_id: str
    total_tasks: int
    completed_tasks: int
    running_tasks: int
    failed_tasks: int
    blocked_tasks: int
    waiting_tasks: int
    cancelled_tasks: int
    completion_percentage: float
    estimated_remaining_seconds: float
    elapsed_seconds: float
    active_task: str = ""
    last_event: str = ""
    task_breakdown: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "running_tasks": self.running_tasks,
            "failed_tasks": self.failed_tasks,
            "blocked_tasks": self.blocked_tasks,
            "waiting_tasks": self.waiting_tasks,
            "cancelled_tasks": self.cancelled_tasks,
            "completion_percentage": self.completion_percentage,
            "estimated_remaining_seconds": self.estimated_remaining_seconds,
            "elapsed_seconds": self.elapsed_seconds,
            "active_task": self.active_task,
            "last_event": self.last_event,
            "task_breakdown": self.task_breakdown,
        }


class ProgressMonitor:
    def __init__(self, scheduler: Scheduler, executor: Executor, event_bus: EventBus) -> None:
        self._scheduler = scheduler
        self._executor = executor
        self._event_bus = event_bus
        self._started_at: datetime | None = None
        self._plan_id: str = ""
        self._last_event: str = ""
        self._event_bus.subscribe_all(self._on_event)

    def start_monitoring(self, plan_id: str) -> None:
        self._plan_id = plan_id
        self._started_at = datetime.now(UTC)

    def _on_event(self, event: Event) -> None:
        if event.type == EventType.TASK_COMPLETED:
            self._last_event = f"Task {event.data.get('task_id', '')} completed"
        elif event.type == EventType.TASK_FAILED:
            self._last_event = f"Task {event.data.get('task_id', '')} failed: {event.data.get('error', '')}"
        elif event.type == EventType.TASK_STARTED:
            self._last_event = f"Task {event.data.get('task_id', '')} started"
        elif event.type == EventType.MILESTONE_REACHED:
            self._last_event = f"Milestone: {event.data.get('milestone', '')}"
        elif event.type == EventType.PLAN_REPLANNED:
            self._last_event = "Plan was replanned"

    def get_progress(self) -> ProgressReport:
        schedule = self._scheduler.schedule()
        task_states = self._scheduler.get_task_summary()
        total = len(task_states)
        completed = len(schedule.completed_tasks)
        running = len(schedule.running_tasks)
        failed = len(schedule.failed_tasks)
        blocked = len(schedule.blocked_tasks)
        waiting = len(schedule.waiting_tasks)
        cancelled = sum(1 for s in task_states.values() if s == "CANCELLED")
        pct = (completed / total * 100) if total > 0 else 0.0
        elapsed = 0.0
        if self._started_at is not None:
            elapsed = (datetime.now(UTC) - self._started_at).total_seconds()
        remaining = self._estimate_remaining(schedule)
        active_task = ""
        if schedule.running_tasks:
            active_task = schedule.running_tasks[0]
        self._event_bus.emit(Event(
            EventType.PROGRESS_UPDATED, self._plan_id,
            {"completion": pct, "completed": completed, "total": total},
        ))
        return ProgressReport(
            plan_id=self._plan_id,
            total_tasks=total,
            completed_tasks=completed,
            running_tasks=running,
            failed_tasks=failed,
            blocked_tasks=blocked,
            waiting_tasks=waiting,
            cancelled_tasks=cancelled,
            completion_percentage=round(pct, 1),
            estimated_remaining_seconds=remaining,
            elapsed_seconds=round(elapsed, 1),
            active_task=active_task,
            last_event=self._last_event,
            task_breakdown=task_states,
        )

    def _estimate_remaining(self, schedule) -> float:
        remaining_tasks = set(
            schedule.ready_queue + schedule.waiting_tasks + schedule.blocked_tasks
        )
        total_remaining_hours = 0.0
        for tid in remaining_tasks:
            task = self._scheduler.graph.tasks.get(tid)
            if task:
                total_remaining_hours += task.estimated_effort_hours
        running = len(schedule.running_tasks)
        parallelism = max(running, 1)
        return (total_remaining_hours / parallelism) * 3600

    def get_summary(self) -> dict[str, Any]:
        progress = self.get_progress()
        return {
            "plan_id": progress.plan_id,
            "progress": progress.to_dict(),
            "events": [e.to_dict() for e in self._event_bus.get_history(self._plan_id)],
        }
