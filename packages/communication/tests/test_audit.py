from __future__ import annotations

import pytest

from jarvis_communication.audit import AuditService
from jarvis_communication.context import ExecutionContext


@pytest.fixture
def service() -> AuditService:
    return AuditService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_log_and_query(service: AuditService, context: ExecutionContext) -> None:
    await service.log("message.sent", "user-1", "message-1", context=context)
    await service.log("message.read", "user-2", "message-1", context=context)
    results = await service.query(action="message.sent", context=context)
    assert len(results) == 1
    assert results[0].actor == "user-1"


@pytest.mark.asyncio
async def test_log_with_details(service: AuditService, context: ExecutionContext) -> None:
    entry = await service.log("test.action", "admin", "resource-1", details={"key": "value"}, success=True, ip_address="127.0.0.1", context=context)
    assert entry.action == "test.action"
    assert entry.actor == "admin"
    assert entry.target == "resource-1"
    assert entry.details["key"] == "value"
    assert entry.ip_address == "127.0.0.1"


@pytest.mark.asyncio
async def test_get_by_id(service: AuditService, context: ExecutionContext) -> None:
    entry = await service.log("test", "user", "target", context=context)
    retrieved = await service.get_by_id(entry.entry_id, context=context)
    assert retrieved is not None
    assert retrieved.entry_id == entry.entry_id


@pytest.mark.asyncio
async def test_count_by_action(service: AuditService, context: ExecutionContext) -> None:
    await service.log("action.a", "user1", "t1", context=context)
    await service.log("action.a", "user2", "t2", context=context)
    await service.log("action.b", "user1", "t3", context=context)
    counts = await service.count_by_action(context=context)
    assert counts["action.a"] == 2
    assert counts["action.b"] == 1


@pytest.mark.asyncio
async def test_count_by_actor(service: AuditService, context: ExecutionContext) -> None:
    await service.log("action.1", "alice", "t1", context=context)
    await service.log("action.2", "alice", "t2", context=context)
    await service.log("action.3", "bob", "t3", context=context)
    counts = await service.count_by_actor(context=context)
    assert counts["alice"] == 2
    assert counts["bob"] == 1
