from __future__ import annotations

import asyncio

from jarvis_core.domain.conversations import (
    Conversation,
    ConversationContext,
    ConversationMetadata,
    ConversationState,
    Message,
)
from jarvis_core.domain.identity import Profile, User
from jarvis_core.domain.shared.value_objects import DomainIdentifier, Email, Timestamp
from jarvis_infrastructure.adapters.cache import InMemoryCacheAdapter
from jarvis_infrastructure.adapters.database import (
    DomainRepositoryAdapter,
    InMemoryRecordStore,
    SQLiteDatabaseAdapter,
)


def _build_conversation() -> Conversation:
    return Conversation(
        id=DomainIdentifier.new(),
        context=ConversationContext(summary="summary"),
        history=(
            Message(
                id=DomainIdentifier.new(),
                author_id=DomainIdentifier.new(),
                content="hello",
                attachments=(),
                created_at=Timestamp.now(),
            ),
        ),
        metadata=ConversationMetadata(topic="topic", tags=("tag",)),
        state=ConversationState.OPEN,
    )


def _build_user() -> User:
    return User(
        id=DomainIdentifier.new(),
        email=Email("jarvis@example.com"),
        profile=Profile(display_name="Jarvis", timezone="UTC"),
        roles=(),
        preferences=(),
        devices=(),
    )


def test_domain_repository_adapter_supports_conversation_and_user_roundtrip() -> None:
    repository = DomainRepositoryAdapter(store=InMemoryRecordStore())

    conversation = _build_conversation()
    user = _build_user()

    repository.save(conversation)
    repository.save_user(user)

    assert repository.get(conversation.id) == conversation
    assert repository.get_user(user.id) == user


def test_sqlite_database_adapter_exposes_repository_contracts() -> None:
    async def _run() -> None:
        adapter = SQLiteDatabaseAdapter(path=":memory:")

        await adapter.start()
        repository = adapter.repositories

        conversation = _build_conversation()
        repository.save(conversation)

        assert repository.get(conversation.id) == conversation

        await adapter.stop()

    asyncio.run(_run())


def test_in_memory_cache_adapter_supports_basic_operations() -> None:
    async def _run() -> None:
        adapter = InMemoryCacheAdapter()

        await adapter.start()
        await adapter.set("alpha", "one")

        assert await adapter.get("alpha") == "one"

        await adapter.delete("alpha")

        assert await adapter.get("alpha") is None

        await adapter.stop()

    asyncio.run(_run())
