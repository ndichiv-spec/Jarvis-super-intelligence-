from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.engine import CommunicationEngine
from jarvis_communication.models import (
    ChannelType,
    CommunicationMessage,
    MessageType,
    Notification,
    NotificationLevel,
    Priority,
)


@pytest.fixture
def engine() -> CommunicationEngine:
    return CommunicationEngine()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_send_message(engine: CommunicationEngine, context: ExecutionContext) -> None:
    msg = CommunicationMessage(
        sender="user-1",
        receiver="JARVIS",
        body="Hello JARVIS",
    )
    sent = await engine.send_message(msg, context=context)
    assert sent.message_id is not None
    assert sent.delivery_status.value == "sent"
    assert sent.sender == "user-1"
    assert sent.receiver == "JARVIS"


@pytest.mark.asyncio
async def test_send_notification(engine: CommunicationEngine, context: ExecutionContext) -> None:
    notification = Notification(
        title="Test Alert",
        body="This is a test",
        level=NotificationLevel.INFO,
        source="test",
        target_user="user-1",
    )
    result = await engine.send_notification(notification, context=context)
    assert result.notification_id is not None
    assert result.title == "Test Alert"
    assert result.level == NotificationLevel.INFO


@pytest.mark.asyncio
async def test_get_metrics_summary(engine: CommunicationEngine) -> None:
    metrics = await engine.get_metrics_summary()
    assert "messages_sent" in metrics
    assert "notifications_sent" in metrics
    assert "active_sessions" in metrics
    assert "conversation_count" in metrics


@pytest.mark.asyncio
async def test_mark_read(engine: CommunicationEngine, context: ExecutionContext) -> None:
    msg = CommunicationMessage(sender="user-1", receiver="user-2", body="Read test")
    sent = await engine.send_message(msg, context=context)
    await engine.mark_read(sent.message_id, "user-2", context=context)
    retrieved = await engine.messaging.get(sent.message_id)
    assert retrieved is not None
    assert retrieved.read_status.value == "read"


@pytest.mark.asyncio
async def test_get_presence(engine: CommunicationEngine) -> None:
    await engine.presence.set_online("user-1")
    status = await engine.get_presence("user-1")
    assert status == "online"
    offline_status = await engine.get_presence("nonexistent")
    assert offline_status == "offline"


@pytest.mark.asyncio
async def test_get_conversation(engine: CommunicationEngine, context: ExecutionContext) -> None:
    conv = await engine.conversations.create("Test Conversation", ("user-1", "JARVIS"), context=context)
    retrieved = await engine.get_conversation(conv.conversation_id, context=context)
    assert retrieved is not None
    assert retrieved.title == "Test Conversation"
    assert "user-1" in retrieved.participants
