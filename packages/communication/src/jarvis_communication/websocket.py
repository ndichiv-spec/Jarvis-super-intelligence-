from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jarvis_communication.models import CommunicationMessage, Notification


WebSocketHandler = Callable[[dict[str, Any]], None]


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocketHandler]] = {}
        self._topics: dict[str, list[WebSocketHandler]] = {}
        self._client_info: dict[str, dict[str, Any]] = {}

    def register_client(
        self,
        client_id: str,
        handler: WebSocketHandler,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self._connections.setdefault(client_id, []).append(handler)
        self._client_info[client_id] = {
            "connected_at": datetime.now(UTC),
            "metadata": metadata or {},
        }
        return client_id

    def unregister_client(self, client_id: str) -> None:
        self._connections.pop(client_id, None)
        self._client_info.pop(client_id, None)
        for topic_handlers in self._topics.values():
            topic_handlers[:] = [
                h for h in topic_handlers
                if h not in self._connections.get(client_id, [])
            ]

    def subscribe_to_topic(
        self,
        client_id: str,
        topic: str,
    ) -> None:
        handlers = self._connections.get(client_id, [])
        for handler in handlers:
            self._topics.setdefault(topic, []).append(handler)

    def unsubscribe_from_topic(
        self,
        client_id: str,
        topic: str,
    ) -> None:
        handlers = self._connections.get(client_id, [])
        topic_handlers = self._topics.get(topic, [])
        for handler in handlers:
            if handler in topic_handlers:
                topic_handlers.remove(handler)

    def broadcast(self, topic: str, data: dict[str, Any]) -> None:
        for handler in self._topics.get(topic, []):
            try:
                handler(data)
            except Exception:
                pass

    def send_to_client(self, client_id: str, data: dict[str, Any]) -> None:
        for handler in self._connections.get(client_id, []):
            try:
                handler(data)
            except Exception:
                pass

    async def broadcast_message(
        self,
        message: CommunicationMessage,
    ) -> None:
        self.broadcast("messages", {
            "type": "message",
            "message_id": message.message_id,
            "sender": message.sender,
            "body": message.body,
            "timestamp": message.timestamp.isoformat(),
        })

    async def broadcast_notification(
        self,
        notification: Notification,
    ) -> None:
        self.broadcast("notifications", {
            "type": "notification",
            "notification_id": notification.notification_id,
            "title": notification.title,
            "body": notification.body,
            "level": notification.level,
            "timestamp": notification.timestamp.isoformat(),
        })

    async def broadcast_presence(
        self,
        user_id: str,
        status: str,
    ) -> None:
        self.broadcast("presence", {
            "type": "presence",
            "user_id": user_id,
            "status": status,
        })

    def get_connected_clients(self) -> list[str]:
        return list(self._connections.keys())

    def get_client_count(self) -> int:
        return len(self._connections)

    @property
    def connection_count(self) -> int:
        return len(self._connections)
