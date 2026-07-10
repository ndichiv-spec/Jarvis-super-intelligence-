from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol, runtime_checkable

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messages import BaseMessage, EventMessage


@dataclass(frozen=True, slots=True)
class EventSnapshot:
    aggregate_id: str
    version: int
    state: Mapping[str, Any]
    captured_at: datetime


@dataclass(frozen=True, slots=True)
class EventRecord:
    version: int
    event: EventMessage
    stored_at: datetime


@runtime_checkable
class EventStore(Protocol):
    async def append(self, event: EventMessage, *, expected_version: int | None = None) -> int: ...

    async def replay(
        self,
        *,
        event_name: str | None = None,
        from_version: int = 0,
    ) -> AsyncIterator[EventRecord]: ...

    async def load_snapshot(self, aggregate_id: str) -> EventSnapshot | None: ...

    async def save_snapshot(self, snapshot: EventSnapshot) -> None: ...


@runtime_checkable
class EventReplayProvider(Protocol):
    def replay(
        self,
        *,
        event_name: str | None = None,
        from_timestamp: datetime | None = None,
    ) -> AsyncIterator[EventMessage]: ...


@runtime_checkable
class DeadLetterSink(Protocol):
    async def publish_dead_letter(
        self,
        message: BaseMessage,
        context: ExecutionContext,
        error: Exception,
    ) -> None: ...


@runtime_checkable
class MessageSerializer(Protocol):
    format_name: str

    def serialize(self, message: BaseMessage) -> bytes: ...

    def deserialize(self, payload: bytes, *, message_type: type[BaseMessage]) -> BaseMessage: ...


@runtime_checkable
class TraceSpan(Protocol):
    def set_attribute(self, key: str, value: Any) -> None: ...

    def add_event(self, event_name: str, attributes: Mapping[str, Any] | None = None) -> None: ...

    def finish(self) -> None: ...


@runtime_checkable
class Tracer(Protocol):
    def start_span(self, span_name: str, context: ExecutionContext) -> TraceSpan: ...


@runtime_checkable
class Logger(Protocol):
    def debug(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

    def info(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

    def warning(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

    def error(self, message: str, *, context: ExecutionContext | None = None) -> None: ...


@runtime_checkable
class Metrics(Protocol):
    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None: ...

    def timing(
        self,
        metric_name: str,
        duration: timedelta,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None: ...


@runtime_checkable
class Diagnostics(Protocol):
    def record_timeline(
        self,
        operation: str,
        context: ExecutionContext,
        timeline: Mapping[str, datetime],
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class CronSchedule:
    expression: str
    timezone: str = "UTC"


@dataclass(frozen=True, slots=True)
class ScheduledMessage:
    message: BaseMessage
    run_at: datetime
    schedule_id: str


@runtime_checkable
class Scheduler(Protocol):
    async def schedule_delayed(self, message: BaseMessage, *, delay: timedelta) -> str: ...

    async def schedule_recurring(self, message: BaseMessage, *, every: timedelta) -> str: ...

    async def schedule_cron(self, message: BaseMessage, *, cron: CronSchedule) -> str: ...

    async def cancel(self, schedule_id: str) -> None: ...
