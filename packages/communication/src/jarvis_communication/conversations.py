from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messaging import MessagingService
from jarvis_communication.models import (
    CommunicationMessage,
    Conversation,
)


class ConversationManager:
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messaging: MessagingService | None = None

    def bind_messaging(self, messaging: MessagingService) -> None:
        self._messaging = messaging

    async def create(
        self,
        title: str,
        participants: tuple[str, ...],
        *,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> Conversation:
        conversation = Conversation(
            title=title,
            participants=participants,
            metadata=metadata or {},
        )
        self._conversations[conversation.conversation_id] = conversation
        return conversation

    async def get(
        self,
        conversation_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Conversation | None:
        return self._conversations.get(conversation_id)

    async def add_message(
        self,
        conversation_id: str,
        message: CommunicationMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> Conversation | None:
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            return None
        updated = Conversation(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            participants=conversation.participants,
            created_at=conversation.created_at,
            updated_at=datetime.now(UTC),
            metadata=conversation.metadata,
            is_archived=conversation.is_archived,
            message_count=conversation.message_count + 1,
        )
        self._conversations[conversation_id] = updated
        return updated

    async def list_by_participant(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Conversation]:
        return [
            conv
            for conv in self._conversations.values()
            if user_id in conv.participants and not conv.is_archived
        ]

    async def archive(
        self,
        conversation_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            return False
        updated = Conversation(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            participants=conversation.participants,
            created_at=conversation.created_at,
            updated_at=datetime.now(UTC),
            metadata=conversation.metadata,
            is_archived=True,
            message_count=conversation.message_count,
        )
        self._conversations[conversation_id] = updated
        return True

    async def add_participant(
        self,
        conversation_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Conversation | None:
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            return None
        if user_id in conversation.participants:
            return conversation
        new_participants = (*conversation.participants, user_id)
        updated = Conversation(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            participants=new_participants,
            created_at=conversation.created_at,
            updated_at=datetime.now(UTC),
            metadata=conversation.metadata,
            is_archived=conversation.is_archived,
            message_count=conversation.message_count,
        )
        self._conversations[conversation_id] = updated
        return updated

    async def remove_participant(
        self,
        conversation_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Conversation | None:
        conversation = self._conversations.get(conversation_id)
        if conversation is None or user_id not in conversation.participants:
            return None
        new_participants = tuple(p for p in conversation.participants if p != user_id)
        updated = Conversation(
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            participants=new_participants,
            created_at=conversation.created_at,
            updated_at=datetime.now(UTC),
            metadata=conversation.metadata,
            is_archived=conversation.is_archived,
            message_count=conversation.message_count,
        )
        self._conversations[conversation_id] = updated
        return updated

    async def search(
        self,
        query: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Conversation]:
        query_lower = query.lower()
        return [
            conv
            for conv in self._conversations.values()
            if query_lower in conv.title.lower()
        ]

    async def get_summary(
        self,
        conversation_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            return {}
        return {
            "conversation_id": conversation.conversation_id,
            "title": conversation.title,
            "participant_count": len(conversation.participants),
            "message_count": conversation.message_count,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "is_archived": conversation.is_archived,
        }

    @property
    def total_conversations(self) -> int:
        return len(self._conversations)
