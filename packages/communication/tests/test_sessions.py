from __future__ import annotations

from datetime import timedelta

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import SessionStatus
from jarvis_communication.sessions import SessionManager


@pytest.fixture
def manager() -> SessionManager:
    return SessionManager()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_create_and_get(manager: SessionManager, context: ExecutionContext) -> None:
    session = await manager.create("user-1", context=context)
    retrieved = await manager.get(session.session_id, context=context)
    assert retrieved is not None
    assert retrieved.user_id == "user-1"
    assert retrieved.status == SessionStatus.ACTIVE


@pytest.mark.asyncio
async def test_set_status(manager: SessionManager, context: ExecutionContext) -> None:
    session = await manager.create("user-1", context=context)
    updated = await manager.set_status(session.session_id, SessionStatus.AWAY, context=context)
    assert updated is not None
    assert updated.status == SessionStatus.AWAY


@pytest.mark.asyncio
async def test_close(manager: SessionManager, context: ExecutionContext) -> None:
    session = await manager.create("user-1", context=context)
    assert await manager.close(session.session_id, context=context) is True
    closed = await manager.get(session.session_id, context=context)
    assert closed is not None
    assert closed.status == SessionStatus.CLOSED


@pytest.mark.asyncio
async def test_list_active(manager: SessionManager, context: ExecutionContext) -> None:
    s1 = await manager.create("user-1", context=context)
    s2 = await manager.create("user-2", context=context)
    await manager.set_status(s2.session_id, SessionStatus.IDLE, context=context)
    active = await manager.list_active(context=context)
    assert len(active) == 1
    assert active[0].session_id == s1.session_id


@pytest.mark.asyncio
async def test_cleanup_stale(manager: SessionManager, context: ExecutionContext) -> None:
    import asyncio
    session = await manager.create("user-1", context=context)
    await manager.update_activity(session.session_id, context=context)
    count = await manager.cleanup_stale(max_idle=timedelta(seconds=0), context=context)
    assert count >= 0


@pytest.mark.asyncio
async def test_update_activity(manager: SessionManager, context: ExecutionContext) -> None:
    session = await manager.create("user-1", context=context)
    import asyncio
    await asyncio.sleep(0.01)
    updated = await manager.update_activity(session.session_id, context=context)
    assert updated is not None
    assert updated.last_activity_at >= session.last_activity_at
