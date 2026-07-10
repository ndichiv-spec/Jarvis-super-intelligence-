from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.email import EmailMessage, EmailService


@pytest.fixture
def service() -> EmailService:
    return EmailService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_send_and_get(service: EmailService, context: ExecutionContext) -> None:
    email = EmailMessage(
        to_addresses=("user@example.com",),
        subject="Hello",
        body_text="Test body",
        sender="system@jarvis.local",
    )
    sent = await service.send(email, context=context)
    assert sent.status == "sent"
    assert sent.sent_at is not None
    retrieved = await service.get(sent.email_id, context=context)
    assert retrieved is not None
    assert retrieved.subject == "Hello"


@pytest.mark.asyncio
async def test_list(service: EmailService, context: ExecutionContext) -> None:
    for i in range(3):
        await service.send(
            EmailMessage(to_addresses=("user@example.com",), subject=f"Email {i}", body_text=f"Body {i}", sender="test@jarvis.local"),
            context=context,
        )
    emails = await service.list(context=context)
    assert len(emails) == 3


@pytest.mark.asyncio
async def test_delete(service: EmailService, context: ExecutionContext) -> None:
    email = EmailMessage(to_addresses=("user@example.com",), subject="Del", body_text="Body", sender="test@jarvis.local")
    sent = await service.send(email, context=context)
    assert await service.delete(sent.email_id, context=context) is True
    assert await service.get(sent.email_id, context=context) is None
