from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Notification, NotificationLevel


class NotificationService:
    def __init__(self) -> None:
        self._notifications: dict[str, Notification] = {}
        self._user_notifications: dict[str, list[str]] = {}

    async def send(
        self,
        notification: Notification,
        *,
        context: ExecutionContext | None = None,
    ) -> Notification:
        ctx = context or ExecutionContext.new(source="notifications")
        self._notifications[notification.notification_id] = notification
        if notification.target_user:
            user_list = self._user_notifications.setdefault(notification.target_user, [])
            user_list.append(notification.notification_id)
        return notification

    async def get(
        self,
        notification_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Notification | None:
        return self._notifications.get(notification_id)

    async def list_by_user(
        self,
        user_id: str,
        *,
        limit: int = 50,
        unread_only: bool = False,
        level: NotificationLevel | None = None,
        context: ExecutionContext | None = None,
    ) -> list[Notification]:
        notification_ids = self._user_notifications.get(user_id, [])
        notifications: list[Notification] = []
        for nid in notification_ids:
            notification = self._notifications.get(nid)
            if notification is None:
                continue
            if unread_only and notification.read:
                continue
            if level is not None and notification.level != level:
                continue
            notifications.append(notification)
        notifications.sort(key=lambda n: n.timestamp, reverse=True)
        return notifications[:limit]

    async def mark_read(
        self,
        notification_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        notification = self._notifications.get(notification_id)
        if notification is None:
            return False
        updated = Notification(
            notification_id=notification.notification_id,
            title=notification.title,
            body=notification.body,
            level=notification.level,
            source=notification.source,
            target_user=notification.target_user,
            target_channel=notification.target_channel,
            timestamp=notification.timestamp,
            read=True,
            metadata=notification.metadata,
            action_url=notification.action_url,
        )
        self._notifications[notification_id] = updated
        return True

    async def mark_all_read(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> int:
        count = 0
        notification_ids = self._user_notifications.get(user_id, [])
        for nid in notification_ids:
            notification = self._notifications.get(nid)
            if notification is not None and not notification.read:
                updated = Notification(
                    notification_id=notification.notification_id,
                    title=notification.title,
                    body=notification.body,
                    level=notification.level,
                    source=notification.source,
                    target_user=notification.target_user,
                    target_channel=notification.target_channel,
                    timestamp=notification.timestamp,
                    read=True,
                    metadata=notification.metadata,
                    action_url=notification.action_url,
                )
                self._notifications[nid] = updated
                count += 1
        return count

    async def count_unread(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> int:
        count = 0
        notification_ids = self._user_notifications.get(user_id, [])
        for nid in notification_ids:
            notification = self._notifications.get(nid)
            if notification is not None and not notification.read:
                count += 1
        return count

    async def delete(
        self,
        notification_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        notification = self._notifications.pop(notification_id, None)
        if notification is None:
            return False
        if notification.target_user and notification.target_user in self._user_notifications:
            user_list = self._user_notifications[notification.target_user]
            if notification_id in user_list:
                user_list.remove(notification_id)
        return True

    async def send_platform_alert(
        self,
        title: str,
        body: str,
        *,
        level: NotificationLevel = NotificationLevel.INFO,
        context: ExecutionContext | None = None,
    ) -> Notification:
        return await self.send(
            Notification(
                title=title,
                body=body,
                level=level,
                source="platform",
            ),
            context=context,
        )

    async def send_task_completion(
        self,
        title: str,
        body: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Notification:
        return await self.send(
            Notification(
                title=title,
                body=body,
                level=NotificationLevel.SUCCESS,
                source="task",
                target_user=user_id,
            ),
            context=context,
        )

    async def send_security_alert(
        self,
        title: str,
        body: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Notification:
        return await self.send(
            Notification(
                title=title,
                body=body,
                level=NotificationLevel.CRITICAL,
                source="security",
            ),
            context=context,
        )

    async def send_agent_update(
        self,
        title: str,
        body: str,
        user_id: str | None = None,
        *,
        context: ExecutionContext | None = None,
    ) -> Notification:
        return await self.send(
            Notification(
                title=title,
                body=body,
                level=NotificationLevel.INFO,
                source="agent",
                target_user=user_id,
            ),
            context=context,
        )

    @property
    def total_notifications(self) -> int:
        return len(self._notifications)
