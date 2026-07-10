from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.conversations import ConversationManager
from jarvis_communication.models import CommunicationMessage


@pytest.fixture
def manager() -> ConversationManager:
    return ConversationManager()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_create_and_get(manager: ConversationManager, context: ExecutionContext) -> None:
    conv = await manager.create("Test", ("user-1", "JARVIS"), context=context)
    retrieved = await manager.get(conv.conversation_id, context=context)
    assert retrieved is not None
    assert retrieved.title == "Test"
    assert len(retrieved.participants) == 2


@pytest.mark.asyncio
async def test_add_message(manager: ConversationManager, context: ExecutionContext) -> None:
    conv = await manager.create("Msg Test", ("user-1", "JARVIS"), context=context)
    msg = CommunicationMessage(sender="user-1", receiver="JARVIS", body="Hello", conversation_id=conv.conversation_id)
    updated = await manager.add_message(conv.conversation_id, msg, context=context)
    assert updated is not None
    assert updated.message_count == 1


@pytest.mark.asyncio
async def test_list_by_participant(manager: ConversationManager, context: ExecutionContext) -> None:
    await manager.create("Conv A", ("user-1", "JARVIS"), context=context)
    await manager.create("Conv B", ("user-2", "JARVIS"), context=context)
    await manager.create("Conv C", ("user-1", "user-2"), context=context)
    user1_convs = await manager.list_by_participant("user-1", context=context)
    assert len(user1_convs) == 2


@pytest.mark.asyncio
async def test_archive(manager: ConversationManager, context: ExecutionContext) -> None:
    conv = await manager.create("Archive Me", ("user-1",), context=context)
    assert await manager.archive(conv.conversation_id, context=context) is True
    archived = await manager.get(conv.conversation_id, context=context)
    assert archived is not None
    assert archived.is_archived is True


@pytest.mark.asyncio
async def test_add_remove_participant(manager: ConversationManager, context: ExecutionContext) -> None:
    conv = await manager.create("Party", ("user-1",), context=context)
    updated = await manager.add_participant(conv.conversation_id, "user-2", context=context)
    assert updated is not None
    assert "user-2" in updated.participants
    updated2 = await manager.remove_participant(conv.conversation_id, "user-2", context=context)
    assert updated2 is not None
    assert "user-2" not in updated2.participants


@pytest.mark.asyncio
async def test_search(manager: ConversationManager, context: ExecutionContext) -> None:
    await manager.create("Project Alpha Design", ("user-1",), context=context)
    await manager.create("Project Beta Planning", ("user-1",), context=context)
    results = await manager.search("Alpha", context=context)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_get_summary(manager: ConversationManager, context: ExecutionContext) -> None:
    conv = await manager.create("Summary Test", ("user-1", "user-2"), context=context)
    summary = await manager.get_summary(conv.conversation_id, context=context)
    assert summary["title"] == "Summary Test"
    assert summary["participant_count"] == 2
    assert summary["message_count"] == 0
