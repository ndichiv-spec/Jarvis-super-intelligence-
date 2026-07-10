from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import AnalyticsEvent


EventHandler = Callable[[AnalyticsEvent], None]


class EventService:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._events: dict[str, AnalyticsEvent] = {}

    def subscribe(self, event_type: str, handler: EventHandler) -> str:
        subscription_id = uuid4().hex
        self._handlers.setdefault(event_type, []).append(handler)
        return subscription_id

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def publish(
        self,
        event_type: str,
        data: dict[str, Any],
        *,
        source: str = "",
        context: ExecutionContext | None = None,
    ) -> AnalyticsEvent:
        event = AnalyticsEvent(
            event_type=event_type,
            data=data,
            source=source,
        )
        self._events[event.event_id] = event
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass
        for handler in self._handlers.get("*", []):
            try:
                handler(event)
            except Exception:
                pass
        return event

    async def get(
        self,
        event_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> AnalyticsEvent | None:
        return self._events.get(event_id)

    async def list_by_type(
        self,
        event_type: str,
        *,
        limit: int = 100,
        context: ExecutionContext | None = None,
    ) -> list[AnalyticsEvent]:
        events = [
            event
            for event in self._events.values()
            if event.event_type == event_type
        ]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    async def list_all(
        self,
        *,
        limit: int = 100,
        context: ExecutionContext | None = None,
    ) -> list[AnalyticsEvent]:
        events = list(self._events.values())
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
