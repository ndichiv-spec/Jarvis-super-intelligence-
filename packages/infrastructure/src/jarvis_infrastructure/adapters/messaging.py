from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    correlation_id: str = ""


@dataclass(frozen=True, slots=True)
class BaseMessage:
    message_name: str
    payload: dict[str, object]


@dataclass(frozen=True, slots=True)
class EventMessage(BaseMessage):
    topic: str | None = None


@dataclass(frozen=True, slots=True)
class EventSnapshot:
    aggregate_id: str
    version: int
    state: dict[str, object]
    captured_at: datetime


@dataclass(frozen=True, slots=True)
class EventRecord:
    version: int
    event: EventMessage
    stored_at: datetime


class EventStore(Protocol):
    async def append(
        self, event: EventMessage, *, expected_version: int | None = None
    ) -> int: ...

    def replay(
        self,
        *,
        event_name: str | None = None,
        from_version: int = 0,
    ) -> AsyncIterator[EventRecord]: ...

    async def load_snapshot(self, aggregate_id: str) -> EventSnapshot | None: ...

    async def save_snapshot(self, snapshot: EventSnapshot) -> None: ...


class DeadLetterSink(Protocol):
    async def publish_dead_letter(
        self,
        message: BaseMessage,
        context: ExecutionContext,
        error: Exception,
    ) -> None: ...

class MessageBrokerClient(Protocol):
    async def publish(self, topic: str, payload: bytes) -> None: ...

    async def ping(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class DeadLetterRecord:
    message: BaseMessage
    context: ExecutionContext
    error_message: str
    occurred_at: datetime


class InMemoryEventStoreAdapter(BaseInfrastructureAdapter, EventStore):
    def __init__(self) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="messaging.event_store.in_memory",
                version="1.0.0",
                provider="in-memory",
                capabilities=("event-store", "snapshots", "replay"),
                configuration_profile="default",
                compatibility=("event-store:v1",),
            )
        )
        self._events: list[EventRecord] = []
        self._snapshots: dict[str, EventSnapshot] = {}

    async def append(self, event: EventMessage, *, expected_version: int | None = None) -> int:
        current_version = len(self._events)
        if expected_version is not None and expected_version != current_version:
            raise ValueError(
                f"Expected version {expected_version}, but current version is {current_version}."
            )
        next_version = current_version + 1
        self._events.append(
            EventRecord(
                version=next_version,
                event=event,
                stored_at=datetime.now(tz=UTC),
            )
        )
        return next_version

    async def replay(
        self,
        *,
        event_name: str | None = None,
        from_version: int = 0,
    ) -> AsyncIterator[EventRecord]:
        for record in self._events:
            if record.version < from_version:
                continue
            if event_name is not None and record.event.message_name != event_name:
                continue
            yield record

    async def load_snapshot(self, aggregate_id: str) -> EventSnapshot | None:
        return self._snapshots.get(aggregate_id)

    async def save_snapshot(self, snapshot: EventSnapshot) -> None:
        self._snapshots[snapshot.aggregate_id] = snapshot

    async def replay_events(
        self,
        *,
        event_name: str | None = None,
        from_timestamp: datetime | None = None,
    ) -> AsyncIterator[EventMessage]:
        async for record in self.replay(event_name=event_name):
            if from_timestamp is not None and record.stored_at < from_timestamp:
                continue
            yield record.event


class InMemoryDeadLetterSink(BaseInfrastructureAdapter, DeadLetterSink):
    def __init__(self) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="messaging.dead_letter.in_memory",
                version="1.0.0",
                provider="in-memory",
                capabilities=("dead-letter",),
                configuration_profile="default",
                compatibility=("dead-letter:v1",),
            )
        )
        self._records: list[DeadLetterRecord] = []

    async def publish_dead_letter(
        self,
        message: BaseMessage,
        context: ExecutionContext,
        error: Exception,
    ) -> None:
        self._records.append(
            DeadLetterRecord(
                message=message,
                context=context,
                error_message=str(error),
                occurred_at=datetime.now(tz=UTC),
            )
        )

    async def records(self) -> tuple[DeadLetterRecord, ...]:
        return tuple(self._records)


class _BrokerAdapter(BaseInfrastructureAdapter):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        client: MessageBrokerClient | None,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("message-broker", "pubsub", "event-dispatch"),
                configuration_profile="default",
                compatibility=("broker:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError(f"{self.adapter_metadata.provider} client is required.")
        await super().start()

    async def publish(self, topic: str, payload: bytes) -> None:
        if self._client is None:
            raise RuntimeError("Broker client is not configured.")
        await self._client.publish(topic, payload)

    async def ping(self) -> bool:
        if self._client is None:
            return False
        return await self._client.ping()


class RedisStreamsBrokerAdapter(_BrokerAdapter):
    def __init__(self, *, client: MessageBrokerClient | None = None) -> None:
        super().__init__(
            identifier="messaging.redis_streams",
            provider="redis-streams",
            client=client,
        )


class KafkaBrokerAdapter(_BrokerAdapter):
    def __init__(self, *, client: MessageBrokerClient | None = None) -> None:
        super().__init__(
            identifier="messaging.kafka",
            provider="kafka",
            client=client,
        )


class RabbitMqBrokerAdapter(_BrokerAdapter):
    def __init__(self, *, client: MessageBrokerClient | None = None) -> None:
        super().__init__(
            identifier="messaging.rabbitmq",
            provider="rabbitmq",
            client=client,
        )


class NatsBrokerAdapter(_BrokerAdapter):
    def __init__(self, *, client: MessageBrokerClient | None = None) -> None:
        super().__init__(
            identifier="messaging.nats",
            provider="nats",
            client=client,
        )
