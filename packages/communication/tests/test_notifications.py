from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Notification, NotificationLevel
from jarvis_communication.notifications import NotificationService


@pytest.fixture
def service() -> NotificationService:
    return NotificationService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_send_and_get(service: NotificationService, context: ExecutionContext) -> None:
    notification = Notification(title="Test", body="Body", level=NotificationLevel.INFO, source="test", target_user="u1")
    result = await service.send(notification, context=context)
    retrieved = await service.get(result.notification_id, context=context)
    assert retrieved is not None
    assert retrieved.title == "Test"


@pytest.mark.asyncio
async def test_list_by_user(service: NotificationService, context: ExecutionContext) -> None:
    for i in range(3):
        await service.send(Notification(title=f"Notif {i}", body=f"Body {i}", source="test", target_user="u1"), context=context)
    await service.send(Notification(title="Other", body="Other", source="test", target_user="u2"), context=context)
    user_notifs = await service.list_by_user("u1", context=context)
    assert len(user_notifs) == 3


@pytest.mark.asyncio
async def test_mark_read(service: NotificationService, context: ExecutionContext) -> None:
    notification = await service.send(Notification(title="Read me", body="Body", source="test", target_user="u1"), context=context)
    assert await service.mark_read(notification.notification_id, context=context) is True
    retrieved = await service.get(notification.notification_id, context=context)
    assert retrieved is not None
    assert retrieved.read is True


@pytest.mark.asyncio
async def test_mark_all_read(service: NotificationService, context: ExecutionContext) -> None:
    for i in range(5):
        await service.send(Notification(title=f"N{i}", body=f"B{i}", source="test", target_user="u1"), context=context)
    count = await service.mark_all_read("u1", context=context)
    assert count == 5
    unread = await service.count_unread("u1", context=context)
    assert unread == 0


@pytest.mark.asyncio
async def test_count_unread(service: NotificationService, context: ExecutionContext) -> None:
    await service.send(Notification(title="Unread", body="Body", source="test", target_user="u1"), context=context)
    assert await service.count_unread("u1", context=context) == 1


@pytest.mark.asyncio
async def test_delete(service: NotificationService, context: ExecutionContext) -> None:
    notification = await service.send(Notification(title="Del", body="Body", source="test", target_user="u1"), context=context)
    assert await service.delete(notification.notification_id, context=context) is True
    assert await service.get(notification.notification_id, context=context) is None


@pytest.mark.asyncio
async def test_send_platform_alert(service: NotificationService, context: ExecutionContext) -> None:
    result = await service.send_platform_alert("Alert", "Body", context=context)
    assert result.source == "platform"
    assert result.level == NotificationLevel.INFO


@pytest.mark.asyncio
async def test_send_security_alert(service: NotificationService, context: ExecutionContext) -> None:
    result = await service.send_security_alert("Security", "Breach detected", context=context)
    assert result.source == "security"
    assert result.level == NotificationLevel.CRITICAL


@pytest.mark.asyncio
async def test_send_task_completion(service: NotificationService, context: ExecutionContext) -> None:
    result = await service.send_task_completion("Task Done", "Completed", "user-1", context=context)
    assert result.source == "task"
    assert result.level == NotificationLevel.SUCCESS
    assert result.target_user == "user-1"


@pytest.mark.asyncio
async def test_send_agent_update(service: NotificationService, context: ExecutionContext) -> None:
    result = await service.send_agent_update("Agent Update", "Status changed", context=context)
    assert result.source == "agent"
