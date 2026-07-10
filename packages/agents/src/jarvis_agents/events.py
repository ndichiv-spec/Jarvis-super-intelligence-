from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_agents.models import AgentEvent


@dataclass(frozen=True, slots=True)
class TypedEvent:
    event_type: str
    payload: str
    source: str
    event_id: str = field(default_factory=lambda: f"evt-{uuid4().hex[:8]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


EventHandler = Callable[[TypedEvent], None]


@dataclass(slots=True)
class EventSystem:
    _handlers: dict[str, list[EventHandler]] = field(default_factory=dict)
    _wildcard_handlers: list[EventHandler] = field(default_factory=list)
    _history: list[TypedEvent] = field(default_factory=list)
    _max_history: int = 1000

    def on(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def on_any(self, handler: EventHandler) -> None:
        self._wildcard_handlers.append(handler)

    def off(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event_type: str, payload: str, source: str) -> TypedEvent:
        event = TypedEvent(event_type=event_type, payload=payload, source=source)
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        for handler in self._wildcard_handlers:
            handler(event)
        for handler in self._handlers.get(event_type, []):
            handler(event)
        return event

    def emit_from_model(self, event: AgentEvent) -> TypedEvent:
        typed = TypedEvent(
            event_type=event.event_type,
            payload=event.payload,
            source=event.source_agent_id,
        )
        self._history.append(typed)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        for handler in self._wildcard_handlers:
            handler(typed)
        for handler in self._handlers.get(event.event_type, []):
            handler(typed)
        return typed

    def history(
        self,
        event_type: str | None = None,
        source: str | None = None,
        limit: int = 100,
    ) -> tuple[TypedEvent, ...]:
        results = self._history
        if event_type is not None:
            results = [e for e in results if e.event_type == event_type]
        if source is not None:
            results = [e for e in results if e.source == source]
        return tuple(results[-limit:])

    def count(self, event_type: str | None = None) -> int:
        if event_type is None:
            return len(self._history)
        return sum(1 for e in self._history if e.event_type == event_type)

    def clear(self) -> None:
        self._history.clear()

    def handler_count(self) -> int:
        return len(self._wildcard_handlers) + sum(len(h) for h in self._handlers.values())
