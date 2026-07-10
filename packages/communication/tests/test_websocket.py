from __future__ import annotations

import pytest

from jarvis_communication.models import CommunicationMessage, Notification
from jarvis_communication.websocket import WebSocketManager


@pytest.fixture
def ws() -> WebSocketManager:
    return WebSocketManager()


def test_register_unregister_client(ws: WebSocketManager) -> None:
    received: list[dict] = []

    def handler(data: dict) -> None:
        received.append(data)

    ws.register_client("client-1", handler)
    assert "client-1" in ws.get_connected_clients()
    assert ws.get_client_count() == 1
    ws.unregister_client("client-1")
    assert ws.get_client_count() == 0


def test_subscribe_broadcast(ws: WebSocketManager) -> None:
    received: list[dict] = []

    def handler(data: dict) -> None:
        received.append(data)

    ws.register_client("client-1", handler)
    ws.subscribe_to_topic("client-1", "messages")
    ws.broadcast("messages", {"text": "hello"})
    assert len(received) == 1
    assert received[0]["text"] == "hello"


def test_unsubscribe_from_topic(ws: WebSocketManager) -> None:
    received: list[dict] = []

    def handler(data: dict) -> None:
        received.append(data)

    ws.register_client("client-1", handler)
    ws.subscribe_to_topic("client-1", "messages")
    ws.unsubscribe_from_topic("client-1", "messages")
    ws.broadcast("messages", {"text": "hello"})
    assert len(received) == 0


def test_send_to_client(ws: WebSocketManager) -> None:
    received: list[dict] = []

    def handler(data: dict) -> None:
        received.append(data)

    ws.register_client("client-1", handler)
    ws.send_to_client("client-1", {"type": "ping"})
    assert len(received) == 1
    assert received[0]["type"] == "ping"


@pytest.mark.asyncio
async def test_broadcast_message(ws: WebSocketManager) -> None:
    received: list[dict] = []

    def handler(data: dict) -> None:
        received.append(data)

    ws.register_client("client-1", handler)
    ws.subscribe_to_topic("client-1", "messages")
    msg = CommunicationMessage(sender="user", receiver="agent", body="Hello")
    await ws.broadcast_message(msg)
    assert len(received) == 1
    assert received[0]["type"] == "message"
    assert received[0]["body"] == "Hello"


@pytest.mark.asyncio
async def test_broadcast_notification(ws: WebSocketManager) -> None:
    received: list[dict] = []

    def handler(data: dict) -> None:
        received.append(data)

    ws.register_client("client-1", handler)
    ws.subscribe_to_topic("client-1", "notifications")
    notification = Notification(title="Test", body="Body", source="test")
    await ws.broadcast_notification(notification)
    assert len(received) == 1
    assert received[0]["type"] == "notification"
    assert received[0]["title"] == "Test"
