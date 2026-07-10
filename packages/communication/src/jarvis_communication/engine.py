from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from datetime import datetime
from typing import Any

from jarvis_communication.analytics import AnalyticsEngine
from jarvis_communication.audit import AuditService
from jarvis_communication.attachments import AttachmentManager
from jarvis_communication.channels import ChannelManager
from jarvis_communication.chat import ChatService
from jarvis_communication.context import ExecutionContext
from jarvis_communication.conversations import ConversationManager
from jarvis_communication.delivery import DeliveryService
from jarvis_communication.email import EmailService
from jarvis_communication.events import EventService
from jarvis_communication.messaging import MessagingService
from jarvis_communication.metrics import MetricsCollector
from jarvis_communication.models import (
    CommunicationMessage,
    Conversation,
    DeliveryStatus,
    Notification,
    ReadStatus,
)
from jarvis_communication.notifications import NotificationService
from jarvis_communication.presence import PresenceService
from jarvis_communication.sessions import SessionManager
from jarvis_communication.streaming import StreamingEngine
from jarvis_communication.subscriptions import SubscriptionManager
from jarvis_communication.templates import TemplateEngine
from jarvis_communication.websocket import WebSocketManager


class CommunicationEngine:
    def __init__(self) -> None:
        self.messaging = MessagingService()
        self.conversations = ConversationManager()
        self.notifications = NotificationService()
        self.email = EmailService()
        self.chat = ChatService()
        self.websocket = WebSocketManager()
        self.events = EventService()
        self.channels = ChannelManager()
        self.sessions = SessionManager()
        self.delivery = DeliveryService()
        self.templates = TemplateEngine()
        self.subscriptions = SubscriptionManager()
        self.attachments = AttachmentManager()
        self.presence = PresenceService()
        self.streaming = StreamingEngine()
        self.audit = AuditService()
        self.analytics = AnalyticsEngine()
        self.metrics = MetricsCollector()

    async def send_message(
        self,
        message: CommunicationMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> CommunicationMessage:
        ctx = context or ExecutionContext.new(source="communication-engine")
        sent = await self.messaging.send(message, context=ctx)
        await self.audit.log("message.sent", message.sender, message.receiver, context=ctx)
        self.metrics.record_message_sent(message.channel)
        return sent

    async def get_conversation(
        self,
        conversation_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Conversation | None:
        ctx = context or ExecutionContext.new(source="communication-engine")
        return await self.conversations.get(conversation_id, context=ctx)

    async def send_notification(
        self,
        notification: Notification,
        *,
        context: ExecutionContext | None = None,
    ) -> Notification:
        ctx = context or ExecutionContext.new(source="communication-engine")
        result = await self.notifications.send(notification, context=ctx)
        self.metrics.record_notification_sent(notification.level)
        return result

    async def get_presence(self, user_id: str) -> str:
        info = await self.presence.get_presence(user_id)
        return info.status.value if info else "offline"

    async def stream_messages(
        self,
        stream_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> AsyncIterator[str]:
        ctx = context or ExecutionContext.new(source="communication-engine")
        async for chunk in self.streaming.subscribe(stream_id, context=ctx):
            yield chunk

    async def get_metrics_summary(self) -> dict[str, Any]:
        return {
            "messages_sent": self.metrics.messages_sent,
            "notifications_sent": self.metrics.notifications_sent,
            "active_sessions": len(self.sessions._sessions),
            "active_presence": len(self.presence._presence),
            "conversation_count": len(self.conversations._conversations),
        }

    async def mark_read(
        self,
        message_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        ctx = context or ExecutionContext.new(source="communication-engine")
        await self.messaging.mark_read(message_id, user_id, context=ctx)
        await self.audit.log("message.read", user_id, message_id, context=ctx)
        self.metrics.record_message_read()
