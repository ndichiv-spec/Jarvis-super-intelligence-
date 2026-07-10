from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Channel, ChannelType, CommunicationMessage, Conversation
from jarvis_communication.security import SecurityService


@pytest.fixture
def security() -> SecurityService:
    return SecurityService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_rate_limit(security: SecurityService, context: ExecutionContext) -> None:
    security.set_rate_limit(3)
    assert await security.check_rate_limit("user-1", context=context) is True
    assert await security.check_rate_limit("user-1", context=context) is True
    assert await security.check_rate_limit("user-1", context=context) is True
    assert await security.check_rate_limit("user-1", context=context) is False


@pytest.mark.asyncio
async def test_rate_limit_status(security: SecurityService, context: ExecutionContext) -> None:
    security.set_rate_limit(10)
    await security.check_rate_limit("user-1", context=context)
    status = await security.get_rate_limit_status("user-1", context=context)
    assert status["current"] == 1
    assert status["limit"] == 10
    assert status["remaining"] == 9


@pytest.mark.asyncio
async def test_validate_message_access(security: SecurityService, context: ExecutionContext) -> None:
    msg = CommunicationMessage(sender="alice", receiver="bob", body="Hello")
    assert await security.validate_message_access("alice", msg, context=context) is True
    assert await security.validate_message_access("bob", msg, context=context) is True
    assert await security.validate_message_access("charlie", msg, context=context) is False


@pytest.mark.asyncio
async def test_validate_channel_access(security: SecurityService, context: ExecutionContext) -> None:
    channel = Channel(name="general", channel_type=ChannelType.INTERNAL, members=("alice", "bob"))
    assert await security.validate_channel_access("alice", channel, context=context) is True
    assert await security.validate_channel_access("charlie", channel, context=context) is False
    system_channel = Channel(name="system", channel_type=ChannelType.SYSTEM)
    assert await security.validate_channel_access("alice", system_channel, context=context) is False


@pytest.mark.asyncio
async def test_validate_conversation_access(security: SecurityService, context: ExecutionContext) -> None:
    conv = Conversation(title="Test", participants=("alice", "bob"))
    assert await security.validate_conversation_access("alice", conv, context=context) is True
    assert await security.validate_conversation_access("charlie", conv, context=context) is False


@pytest.mark.asyncio
async def test_encrypt_decrypt(security: SecurityService, context: ExecutionContext) -> None:
    encrypted = await security.encrypt_payload("secret-data", context=context)
    assert encrypted.startswith("encrypted:")
    decrypted = await security.decrypt_payload(encrypted, context=context)
    assert decrypted == "secret-data"


@pytest.mark.asyncio
async def test_permission_check(security: SecurityService, context: ExecutionContext) -> None:
    def admin_check(user_id: str, _perm: str, _res: str) -> bool:
        return user_id == "admin"
    security.register_permission_check("admin.access", admin_check)
    assert await security.check_permission("admin", "admin.access", "resource", context=context) is True
    assert await security.check_permission("user", "admin.access", "resource", context=context) is False
