from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import (
    CommunicationMessage,
    Conversation,
    DeliveryReceipt,
    DeliveryStatus,
    ReadStatus,
)


class MessagingService:
    def __init__(self) -> None:
        self._messages: dict[str, CommunicationMessage] = {}
        self._receipts: dict[str, list[DeliveryReceipt]] = {}
        self._read_by: dict[str, set[str]] = {}

    async def send(
        self,
        message: CommunicationMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> CommunicationMessage:
        ctx = context or ExecutionContext.new(source="messaging")
        updated = CommunicationMessage(
            message_id=message.message_id,
            sender=message.sender,
            receiver=message.receiver,
            channel=message.channel,
            conversation_id=message.conversation_id,
            timestamp=message.timestamp,
            message_type=message.message_type,
            priority=message.priority,
            body=message.body,
            subject=message.subject,
            attachments=message.attachments,
            metadata=message.metadata,
            delivery_status=DeliveryStatus.SENT,
            read_status=ReadStatus.UNREAD,
        )
        self._messages[updated.message_id] = updated
        return updated

    async def get(
        self,
        message_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> CommunicationMessage | None:
        return self._messages.get(message_id)

    async def list_by_conversation(
        self,
        conversation_id: str,
        *,
        limit: int = 50,
        before: datetime | None = None,
        context: ExecutionContext | None = None,
    ) -> list[CommunicationMessage]:
        messages = [
            msg
            for msg in self._messages.values()
            if msg.conversation_id == conversation_id
        ]
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        if before:
            messages = [m for m in messages if m.timestamp < before]
        return messages[:limit]

    async def list_by_sender(
        self,
        sender: str,
        *,
        limit: int = 50,
        context: ExecutionContext | None = None,
    ) -> list[CommunicationMessage]:
        messages = [
            msg for msg in self._messages.values() if msg.sender == sender
        ]
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return messages[:limit]

    async def list_by_receiver(
        self,
        receiver: str,
        *,
        limit: int = 50,
        context: ExecutionContext | None = None,
    ) -> list[CommunicationMessage]:
        messages = [
            msg for msg in self._messages.values() if msg.receiver == receiver
        ]
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return messages[:limit]

    async def mark_read(
        self,
        message_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        read_set = self._read_by.setdefault(message_id, set())
        read_set.add(user_id)
        message = self._messages.get(message_id)
        if message is not None:
            updated = CommunicationMessage(
                message_id=message.message_id,
                sender=message.sender,
                receiver=message.receiver,
                channel=message.channel,
                conversation_id=message.conversation_id,
                timestamp=message.timestamp,
                message_type=message.message_type,
                priority=message.priority,
                body=message.body,
                subject=message.subject,
                attachments=message.attachments,
                metadata=message.metadata,
                delivery_status=DeliveryStatus.READ,
                read_status=ReadStatus.READ,
            )
            self._messages[message_id] = updated

    async def get_receipts(
        self,
        message_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[DeliveryReceipt]:
        return self._receipts.get(message_id, [])

    async def delete(
        self,
        message_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        return self._messages.pop(message_id, None) is not None

    async def search(
        self,
        query: str,
        *,
        limit: int = 50,
        context: ExecutionContext | None = None,
    ) -> list[CommunicationMessage]:
        results: list[CommunicationMessage] = []
        query_lower = query.lower()
        for msg in self._messages.values():
            if query_lower in msg.body.lower() or (msg.subject and query_lower in msg.subject.lower()):
                results.append(msg)
        results.sort(key=lambda m: m.timestamp, reverse=True)
        return results[:limit]

    @property
    def total_messages(self) -> int:
        return len(self._messages)

    async def count_unread(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> int:
        unread = 0
        for msg in self._messages.values():
            if msg.receiver == user_id and msg.read_status == ReadStatus.UNREAD:
                unread += 1
        return unread
