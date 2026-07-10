from __future__ import annotations

import pytest

from jarvis_communication.events import EventService


@pytest.fixture
def service() -> EventService:
    return EventService()


@pytest.mark.asyncio
async def test_publish_and_list(service: EventService) -> None:
    event = await service.publish("message.sent", {"text": "hello"}, source="test")
    assert event.event_type == "message.sent"
    events = await service.list_by_type("message.sent")
    assert len(events) == 1


@pytest.mark.asyncio
async def test_subscribe_handler(service: EventService) -> None:
    received: list[str] = []

    def handler(event) -> None:
        received.append(event.event_type)

    service.subscribe("custom.event", handler)
    await service.publish("custom.event", {"data": 1})
    assert len(received) == 1
    assert received[0] == "custom.event"


@pytest.mark.asyncio
async def test_wildcard_subscriber(service: EventService) -> None:
    received: list[str] = []

    def handler(event) -> None:
        received.append(event.event_type)

    service.subscribe("*", handler)
    await service.publish("event.a", {})
    await service.publish("event.b", {})
    assert len(received) == 2


@pytest.mark.asyncio
async def test_get_event(service: EventService) -> None:
    event = await service.publish("test.event", {"key": "value"}, source="src")
    retrieved = await service.get(event.event_id)
    assert retrieved is not None
    assert retrieved.event_type == "test.event"
    assert retrieved.source == "src"
