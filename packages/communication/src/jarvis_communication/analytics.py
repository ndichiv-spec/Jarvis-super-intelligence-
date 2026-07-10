from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import AnalyticsEvent


class AnalyticsEngine:
    def __init__(self) -> None:
        self._events: list[AnalyticsEvent] = []

    async def track(
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
        self._events.append(event)
        return event

    async def query(
        self,
        *,
        event_type: str | None = None,
        source: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        context: ExecutionContext | None = None,
    ) -> list[AnalyticsEvent]:
        results: list[AnalyticsEvent] = list(self._events)
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if source:
            results = [e for e in results if e.source == source]
        if since:
            results = [e for e in results if e.timestamp >= since]
        if until:
            results = [e for e in results if e.timestamp <= until]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    async def get_event_counts(
        self,
        *,
        since: datetime | None = None,
        context: ExecutionContext | None = None,
    ) -> dict[str, int]:
        events = self._events
        if since:
            events = [e for e in events if e.timestamp >= since]
        counts: dict[str, int] = {}
        for event in events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts

    async def get_source_counts(
        self,
        *,
        since: datetime | None = None,
        context: ExecutionContext | None = None,
    ) -> dict[str, int]:
        events = self._events
        if since:
            events = [e for e in events if e.timestamp >= since]
        counts: dict[str, int] = {}
        for event in events:
            counts[event.source] = counts.get(event.source, 0) + 1
        return counts

    async def get_message_statistics(
        self,
        *,
        since: datetime | None = None,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        events = self._events
        if since:
            events = [e for e in events if e.timestamp >= since]
        message_events = [e for e in events if "message" in e.event_type]
        return {
            "total_messages": len(message_events),
            "by_type": {
                e.event_type: sum(1 for ev in message_events if ev.event_type == e.event_type)
                for e in message_events
            } if message_events else {},
        }

    async def get_notification_statistics(
        self,
        *,
        since: datetime | None = None,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        events = self._events
        if since:
            events = [e for e in events if e.timestamp >= since]
        notification_events = [e for e in events if "notification" in e.event_type]
        return {
            "total_notifications": len(notification_events),
        }

    async def get_response_latency(
        self,
        *,
        since: datetime | None = None,
        context: ExecutionContext | None = None,
    ) -> dict[str, float]:
        events = self._events
        if since:
            events = [e for e in events if e.timestamp >= since]
        latency_events = [
            e for e in events
            if "latency" in e.event_type and "value_ms" in e.data
        ]
        if not latency_events:
            return {"avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0, "count": 0}
        values = [e.data["value_ms"] for e in latency_events]
        return {
            "avg_ms": sum(values) / len(values),
            "min_ms": min(values),
            "max_ms": max(values),
            "count": len(values),
        }

    @property
    def total_events(self) -> int:
        return len(self._events)
