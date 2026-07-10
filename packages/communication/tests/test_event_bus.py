import asyncio
from collections.abc import Coroutine
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.contracts import DeadLetterSink
from jarvis_communication.event_bus import EventBus
from jarvis_communication.messages import BaseMessage, EventMessage


def _run[T](coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro)


def test_event_bus_publish_with_priority_filter_and_once_subscription() -> None:
    bus = EventBus()
    context = ExecutionContext.new(source="test")
    calls: list[str] = []

    async def high_handler(event: EventMessage, _: ExecutionContext) -> None:
        calls.append(f"high:{event.message_name}")

    async def low_handler(event: EventMessage, _: ExecutionContext) -> None:
        calls.append(f"low:{event.message_name}")

    async def filtered_handler(event: EventMessage, _: ExecutionContext) -> None:
        calls.append(f"filtered:{event.message_name}")

    async def one_time_handler(event: EventMessage, _: ExecutionContext) -> None:
        calls.append(f"once:{event.message_name}")

    bus.subscribe(low_handler, event_name="event.user.created", priority=1)
    bus.subscribe(high_handler, event_name="event.user.created", priority=10)
    bus.subscribe(
        filtered_handler,
        event_filter=lambda event, _ctx: event.payload.get("send") is True,
    )
    bus.subscribe_once(one_time_handler, event_name="event.user.created")

    _run(
        bus.publish(
            EventMessage(
                message_name="event.user.created",
                payload={"send": False},
            ),
            context=context,
        )
    )
    _run(
        bus.publish(
            EventMessage(
                message_name="event.user.created",
                payload={"send": True},
            ),
            context=context,
        )
    )

    assert calls[0:2] == ["high:event.user.created", "low:event.user.created"]
    assert "once:event.user.created" in calls
    assert calls.count("once:event.user.created") == 1
    assert calls.count("filtered:event.user.created") == 1


def test_event_bus_dead_letter_contract_is_invoked() -> None:
    dead_letters: list[str] = []

    class InMemoryDeadLetterSink(DeadLetterSink):
        async def publish_dead_letter(
            self,
            message: BaseMessage,
            context: ExecutionContext,
            error: Exception,
        ) -> None:
            dead_letters.append(f"{message.message_name}:{context.correlation_id}:{error}")

    bus = EventBus(dead_letter_sink=InMemoryDeadLetterSink())

    async def broken_handler(_: EventMessage, __: ExecutionContext) -> None:
        raise RuntimeError("handler failed")

    bus.subscribe(broken_handler)
    _run(
        bus.publish(
            EventMessage(message_name="event.broken"),
            context=ExecutionContext.new(source="test"),
        )
    )

    assert len(dead_letters) == 1
    assert dead_letters[0].startswith("event.broken:")
