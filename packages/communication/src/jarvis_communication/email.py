from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Attachment


@dataclass(frozen=True, slots=True)
class EmailMessage:
    email_id: str = field(default_factory=lambda: __import__("uuid").uuid4().hex)
    to_addresses: tuple[str, ...] = ()
    cc_addresses: tuple[str, ...] = ()
    bcc_addresses: tuple[str, ...] = ()
    subject: str = ""
    body_text: str = ""
    body_html: str | None = None
    sender: str = ""
    attachments: tuple[Attachment, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    sent_at: datetime | None = None
    status: str = "draft"


class EmailService:
    def __init__(self) -> None:
        self._emails: dict[str, EmailMessage] = {}

    async def send(
        self,
        email: EmailMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> EmailMessage:
        ctx = context or ExecutionContext.new(source="email")
        sent = EmailMessage(
            email_id=email.email_id,
            to_addresses=email.to_addresses,
            cc_addresses=email.cc_addresses,
            bcc_addresses=email.bcc_addresses,
            subject=email.subject,
            body_text=email.body_text,
            body_html=email.body_html,
            sender=email.sender,
            attachments=email.attachments,
            metadata=email.metadata,
            sent_at=datetime.now(UTC),
            status="sent",
        )
        self._emails[sent.email_id] = sent
        return sent

    async def get(
        self,
        email_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> EmailMessage | None:
        return self._emails.get(email_id)

    async def list(
        self,
        *,
        limit: int = 50,
        context: ExecutionContext | None = None,
    ) -> list[EmailMessage]:
        emails = list(self._emails.values())
        emails.sort(key=lambda e: e.sent_at or datetime.min.replace(tzinfo=UTC), reverse=True)
        return emails[:limit]

    async def delete(
        self,
        email_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        return self._emails.pop(email_id, None) is not None
