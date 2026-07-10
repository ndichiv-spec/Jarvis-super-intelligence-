from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messaging import MessagingService
from jarvis_communication.models import (
    ChannelType,
    CommunicationMessage,
    MessageType,
    Priority,
    ReadStatus,
)


@pytest.fixture
def messaging() -> MessagingService:
    return MessagingService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_send_and_get(messaging: MessagingService, context: ExecutionContext) -> None:
    msg = CommunicationMessage(sender="user-1", receiver="JARVIS", body="Hello")
    sent = await messaging.send(msg, context=context)
    retrieved = await messaging.get(sent.message_id, context=context)
    assert retrieved is not None
    assert retrieved.body == "Hello"


@pytest.mark.asyncio
async def test_list_by_conversation(messaging: MessagingService, context: ExecutionContext) -> None:
    msgs = [
        CommunicationMessage(sender="u1", receiver="u2", body=f"Msg {i}", conversation_id="conv-1")
        for i in range(5)
    ]
    for m in msgs:
        await messaging.send(m, context=context)
    result = await messaging.list_by_conversation("conv-1", context=context)
    assert len(result) == 5


@pytest.mark.asyncio
async def test_list_by_sender(messaging: MessagingService, context: ExecutionContext) -> None:
    await messaging.send(CommunicationMessage(sender="alice", receiver="bob", body="Hi"), context=context)
    await messaging.send(CommunicationMessage(sender="alice", receiver="charlie", body="Hello"), context=context)
    await messaging.send(CommunicationMessage(sender="bob", receiver="alice", body="Hey"), context=context)
    alice_msgs = await messaging.list_by_sender("alice", context=context)
    assert len(alice_msgs) == 2


@pytest.mark.asyncio
async def test_mark_read(messaging: MessagingService, context: ExecutionContext) -> None:
    msg = CommunicationMessage(sender="u1", receiver="u2", body="Read me")
    sent = await messaging.send(msg, context=context)
    await messaging.mark_read(sent.message_id, "u2", context=context)
    retrieved = await messaging.get(sent.message_id, context=context)
    assert retrieved is not None
    assert retrieved.read_status == ReadStatus.READ


@pytest.mark.asyncio
async def test_search(messaging: MessagingService, context: ExecutionContext) -> None:
    await messaging.send(CommunicationMessage(sender="u1", receiver="u2", body="hello world"), context=context)
    await messaging.send(CommunicationMessage(sender="u1", receiver="u2", body="goodbye world"), context=context)
    results = await messaging.search("hello", context=context)
    assert len(results) == 1
    assert results[0].body == "hello world"


@pytest.mark.asyncio
async def test_count_unread(messaging: MessagingService, context: ExecutionContext) -> None:
    await messaging.send(CommunicationMessage(sender="u1", receiver="u2", body="Unread 1"), context=context)
    await messaging.send(CommunicationMessage(sender="u1", receiver="u2", body="Unread 2"), context=context)
    count = await messaging.count_unread("u2", context=context)
    assert count == 2


@pytest.mark.asyncio
async def test_delete(messaging: MessagingService, context: ExecutionContext) -> None:
    msg = CommunicationMessage(sender="u1", receiver="u2", body="Delete me")
    sent = await messaging.send(msg, context=context)
    assert await messaging.delete(sent.message_id, context=context) is True
    assert await messaging.get(sent.message_id, context=context) is None
