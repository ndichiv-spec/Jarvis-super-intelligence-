from __future__ import annotations

import pytest

from jarvis_communication.channels import ChannelManager
from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import ChannelType


@pytest.fixture
def manager() -> ChannelManager:
    return ChannelManager()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_create_and_get(manager: ChannelManager, context: ExecutionContext) -> None:
    channel = await manager.create("general", ChannelType.INTERNAL, context=context)
    retrieved = await manager.get(channel.channel_id, context=context)
    assert retrieved is not None
    assert retrieved.name == "general"
    assert retrieved.is_active is True


@pytest.mark.asyncio
async def test_list_by_type(manager: ChannelManager, context: ExecutionContext) -> None:
    await manager.create("internal-chat", ChannelType.INTERNAL, context=context)
    await manager.create("ai-chat", ChannelType.AI_CONVERSATION, context=context)
    await manager.create("system-alerts", ChannelType.SYSTEM, context=context)
    internal = await manager.list(channel_type=ChannelType.INTERNAL, context=context)
    assert len(internal) == 1
    all_channels = await manager.list(context=context)
    assert len(all_channels) == 3


@pytest.mark.asyncio
async def test_add_remove_member(manager: ChannelManager, context: ExecutionContext) -> None:
    channel = await manager.create("team", ChannelType.INTERNAL, context=context)
    updated = await manager.add_member(channel.channel_id, "user-1", context=context)
    assert updated is not None
    assert "user-1" in updated.members
    updated2 = await manager.remove_member(channel.channel_id, "user-1", context=context)
    assert updated2 is not None
    assert "user-1" not in updated2.members


@pytest.mark.asyncio
async def test_deactivate(manager: ChannelManager, context: ExecutionContext) -> None:
    channel = await manager.create("temp", ChannelType.INTERNAL, context=context)
    assert await manager.deactivate(channel.channel_id, context=context) is True
    deactivated = await manager.get(channel.channel_id, context=context)
    assert deactivated is not None
    assert deactivated.is_active is False
