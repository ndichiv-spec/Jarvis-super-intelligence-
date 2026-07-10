from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class TelemetryEvent:
    event_type: str
    plan_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetrics:
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration_seconds: float = 0.0
    avg_duration_seconds: float = 0.0
    decisions_made: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    agents_used: list[str] = field(default_factory=list)
    last_execution_time: datetime | None = None


class TelemetryEngine:
    def __init__(self) -> None:
        self._events: list[TelemetryEvent] = []
        self._metrics: dict[str, ExecutionMetrics] = {}
        self._global_metrics = ExecutionMetrics()

    def record_execution(self, plan_id: str, report: Any) -> None:
        metrics = self._metrics.get(plan_id) or ExecutionMetrics()
        metrics.total_executions += 1
        metrics.successful_executions += 1 if report.completed_tasks == report.total_tasks else 0
        metrics.failed_executions += 1 if report.failed_tasks > 0 else 0
        metrics.total_duration_seconds += getattr(report, 'duration_seconds', 0)
        metrics.decisions_made += getattr(report, 'decisions_made', 0)
        metrics.tasks_completed += getattr(report, 'completed_tasks', 0)
        metrics.tasks_failed += getattr(report, 'failed_tasks', 0)
        metrics.last_execution_time = datetime.now(UTC)

        avg_exec = max(1, metrics.total_executions)
        metrics.avg_duration_seconds = metrics.total_duration_seconds / avg_exec
        self._metrics[plan_id] = metrics

        self._global_metrics.total_executions += 1
        self._global_metrics.total_duration_seconds += getattr(report, 'duration_seconds', 0)
        self._global_metrics.decisions_made += getattr(report, 'decisions_made', 0)
        self._global_metrics.tasks_completed += getattr(report, 'completed_tasks', 0)
        self._global_metrics.tasks_failed += getattr(report, 'failed_tasks', 0)

        event = TelemetryEvent(event_type="execution_completed", plan_id=plan_id, data={
            "duration_seconds": getattr(report, 'duration_seconds', 0),
            "completed": getattr(report, 'completed_tasks', 0),
            "failed": getattr(report, 'failed_tasks', 0),
            "decisions": getattr(report, 'decisions_made', 0),
        })
        self._events.append(event)

    def record_event(self, event_type: str, plan_id: str, data: dict[str, Any] | None = None) -> None:
        self._events.append(TelemetryEvent(event_type=event_type, plan_id=plan_id, data=data or {}))

    def get_metrics(self, plan_id: str | None = None) -> ExecutionMetrics:
        if plan_id is not None:
            return self._metrics.get(plan_id) or ExecutionMetrics()
        return self._global_metrics

    def get_events(self, limit: int = 100) -> list[TelemetryEvent]:
        return sorted(self._events, key=lambda e: e.timestamp, reverse=True)[:limit]
