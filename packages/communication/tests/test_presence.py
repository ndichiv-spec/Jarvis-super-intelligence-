from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import PresenceStatus
from jarvis_communication.presence import PresenceService


@pytest.fixture
def service() -> PresenceService:
    return PresenceService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_set_online(service: PresenceService, context: ExecutionContext) -> None:
    info = await service.set_online("user-1", context=context)
    assert info.user_id == "user-1"
    assert info.status == PresenceStatus.ONLINE


@pytest.mark.asyncio
async def test_set_away(service: PresenceService, context: ExecutionContext) -> None:
    info = await service.set_away("user-1", context=context)
    assert info.status == PresenceStatus.AWAY


@pytest.mark.asyncio
async def test_set_busy(service: PresenceService, context: ExecutionContext) -> None:
    info = await service.set_busy("user-1", context=context)
    assert info.status == PresenceStatus.BUSY


@pytest.mark.asyncio
async def test_set_offline(service: PresenceService, context: ExecutionContext) -> None:
    await service.set_online("user-1", context=context)
    info = await service.set_offline("user-1", context=context)
    assert info.status == PresenceStatus.OFFLINE


@pytest.mark.asyncio
async def test_get_presence(service: PresenceService, context: ExecutionContext) -> None:
    await service.set_online("user-1", context=context)
    info = await service.get_presence("user-1", context=context)
    assert info is not None
    assert info.status == PresenceStatus.ONLINE
    unknown = await service.get_presence("unknown", context=context)
    assert unknown is None


@pytest.mark.asyncio
async def test_list_online(service: PresenceService, context: ExecutionContext) -> None:
    await service.set_online("user-1", context=context)
    await service.set_busy("user-2", context=context)
    await service.set_offline("user-3", context=context)
    online = await service.list_online(context=context)
    assert len(online) == 2


@pytest.mark.asyncio
async def test_update_activity(service: PresenceService, context: ExecutionContext) -> None:
    await service.set_online("user-1", context=context)
    info = await service.update_activity("user-1", "Working on project", context=context)
    assert info is not None
    assert info.current_activity == "Working on project"


@pytest.mark.asyncio
async def test_online_count(service: PresenceService) -> None:
    assert service.online_count == 0
