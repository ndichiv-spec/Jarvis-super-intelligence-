from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable


class EventType(Enum):
    PLAN_CREATED = "plan.created"
    PLAN_STARTED = "plan.started"
    PLAN_PAUSED = "plan.paused"
    PLAN_RESUMED = "plan.resumed"
    PLAN_COMPLETED = "plan.completed"
    PLAN_FAILED = "plan.failed"
    PLAN_CANCELLED = "plan.cancelled"
    PLAN_REPLANNED = "plan.replanned"
    TASK_CREATED = "task.created"
    TASK_STATE_CHANGED = "task.state_changed"
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_BLOCKED = "task.blocked"
    AGENT_ASSIGNED = "agent.assigned"
    AGENT_CHANGED = "agent.changed"
    DEPENDENCY_RESOLVED = "dependency.resolved"
    DEPENDENCY_BLOCKED = "dependency.blocked"
    MILESTONE_REACHED = "milestone.reached"
    PROGRESS_UPDATED = "progress.updated"
    PLAN_VALIDATED = "plan.validated"
    PLAN_INVALID = "plan.invalid"
    ERROR = "error"


@dataclass
class Event:
    type: EventType
    plan_id: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "plan_id": self.plan_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


EventHandler = Callable[[Event], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = {}
        self._wildcard_handlers: list[EventHandler] = []
        self._history: list[Event] = []

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._wildcard_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: Event) -> None:
        self._history.append(event)
        for handler in self._wildcard_handlers:
            handler(event)
        for handler in self._handlers.get(event.type, []):
            handler(event)

    def get_history(self, plan_id: str | None = None, event_type: EventType | None = None) -> list[Event]:
        result = self._history
        if plan_id is not None:
            result = [e for e in result if e.plan_id == plan_id]
        if event_type is not None:
            result = [e for e in result if e.type == event_type]
        return result

    def clear(self) -> None:
        self._history.clear()
