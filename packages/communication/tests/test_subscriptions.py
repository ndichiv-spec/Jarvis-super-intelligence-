from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import SubscriptionType
from jarvis_communication.subscriptions import SubscriptionManager


@pytest.fixture
def manager() -> SubscriptionManager:
    return SubscriptionManager()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_subscribe_and_get(manager: SubscriptionManager, context: ExecutionContext) -> None:
    sub = await manager.subscribe("user-1", SubscriptionType.CHANNEL, "channel-1", context=context)
    retrieved = await manager.get(sub.subscription_id, context=context)
    assert retrieved is not None
    assert retrieved.subscriber_id == "user-1"
    assert retrieved.target_id == "channel-1"


@pytest.mark.asyncio
async def test_unsubscribe(manager: SubscriptionManager, context: ExecutionContext) -> None:
    sub = await manager.subscribe("user-1", SubscriptionType.TOPIC, "topic-1", context=context)
    assert await manager.unsubscribe(sub.subscription_id, context=context) is True
    assert await manager.get(sub.subscription_id, context=context) is None


@pytest.mark.asyncio
async def test_list_by_subscriber(manager: SubscriptionManager, context: ExecutionContext) -> None:
    await manager.subscribe("user-1", SubscriptionType.CHANNEL, "ch-1", context=context)
    await manager.subscribe("user-1", SubscriptionType.CHANNEL, "ch-2", context=context)
    await manager.subscribe("user-2", SubscriptionType.CHANNEL, "ch-1", context=context)
    user1_subs = await manager.list_by_subscriber("user-1", context=context)
    assert len(user1_subs) == 2


@pytest.mark.asyncio
async def test_list_by_target(manager: SubscriptionManager, context: ExecutionContext) -> None:
    await manager.subscribe("user-1", SubscriptionType.CONVERSATION, "conv-1", context=context)
    await manager.subscribe("user-2", SubscriptionType.CONVERSATION, "conv-1", context=context)
    subs = await manager.list_by_target("conv-1", context=context)
    assert len(subs) == 2


@pytest.mark.asyncio
async def test_list_subscribers(manager: SubscriptionManager, context: ExecutionContext) -> None:
    await manager.subscribe("alice", SubscriptionType.TOPIC, "topic-x", context=context)
    await manager.subscribe("bob", SubscriptionType.TOPIC, "topic-x", context=context)
    subscribers = await manager.list_subscribers("topic-x", context=context)
    assert "alice" in subscribers
    assert "bob" in subscribers


@pytest.mark.asyncio
async def test_deactivate(manager: SubscriptionManager, context: ExecutionContext) -> None:
    sub = await manager.subscribe("user-1", SubscriptionType.CHANNEL, "ch-1", context=context)
    assert await manager.deactivate(sub.subscription_id, context=context) is True
    deactivated = await manager.get(sub.subscription_id, context=context)
    assert deactivated is not None
    assert deactivated.active is False
