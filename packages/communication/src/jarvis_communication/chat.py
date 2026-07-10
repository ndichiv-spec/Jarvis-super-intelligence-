from __future__ import annotations

from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messaging import MessagingService
from jarvis_communication.models import (
    ChannelType,
    CommunicationMessage,
    MessageType,
    Priority,
)


class ChatService:
    def __init__(self) -> None:
        self._messaging: MessagingService | None = None

    def bind_messaging(self, messaging: MessagingService) -> None:
        self._messaging = messaging

    async def send_message(
        self,
        sender: str,
        receiver: str,
        body: str,
        *,
        conversation_id: str | None = None,
        priority: Priority = Priority.NORMAL,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> CommunicationMessage:
        msg = CommunicationMessage(
            sender=sender,
            receiver=receiver,
            channel=ChannelType.INTERNAL,
            conversation_id=conversation_id,
            message_type=MessageType.TEXT,
            priority=priority,
            body=body,
            metadata=metadata or {},
        )
        if self._messaging is not None:
            return await self._messaging.send(msg, context=context)
        return msg

    async def send_ai_message(
        self,
        sender: str,
        receiver: str,
        body: str,
        *,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> CommunicationMessage:
        msg = CommunicationMessage(
            sender=sender,
            receiver=receiver,
            channel=ChannelType.AI_CONVERSATION,
            conversation_id=conversation_id,
            message_type=MessageType.TEXT,
            body=body,
            metadata=metadata or {},
        )
        if self._messaging is not None:
            return await self._messaging.send(msg, context=context)
        return msg

    async def send_system_message(
        self,
        receiver: str,
        body: str,
        *,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> CommunicationMessage:
        msg = CommunicationMessage(
            sender="system",
            receiver=receiver,
            channel=ChannelType.SYSTEM,
            conversation_id=conversation_id,
            message_type=MessageType.SYSTEM,
            body=body,
            metadata=metadata or {},
        )
        if self._messaging is not None:
            return await self._messaging.send(msg, context=context)
        return msg
