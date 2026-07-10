from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Attachment


SUPPORTED_TYPES: dict[str, tuple[str, ...]] = {
    "pdf": ("application/pdf",),
    "image": ("image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"),
    "document": (
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
    ),
    "audio": ("audio/mpeg", "audio/wav", "audio/ogg", "audio/flac"),
    "video": ("video/mp4", "video/webm", "video/ogg"),
    "code": (
        "text/x-python",
        "text/javascript",
        "text/typescript",
        "text/x-java",
        "text/x-c",
        "text/x-c++",
        "text/html",
        "text/css",
        "application/json",
        "application/xml",
        "text/x-yaml",
        "text/x-toml",
        "text/x-rust",
        "text/x-go",
        "text/x-ruby",
        "text/x-php",
    ),
    "archive": (
        "application/zip",
        "application/x-tar",
        "application/gzip",
        "application/x-7z-compressed",
        "application/x-rar-compressed",
    ),
}


def classify_content_type(content_type: str) -> str:
    for category, types in SUPPORTED_TYPES.items():
        if content_type in types:
            return category
    return "other"


class AttachmentManager:
    def __init__(self) -> None:
        self._attachments: dict[str, Attachment] = {}

    async def store(
        self,
        filename: str,
        content_type: str,
        size: int,
        storage_path: str,
        *,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> Attachment:
        attachment = Attachment(
            filename=filename,
            content_type=content_type,
            size=size,
            storage_path=storage_path,
            metadata=metadata or {},
        )
        self._attachments[attachment.attachment_id] = attachment
        return attachment

    async def get(
        self,
        attachment_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Attachment | None:
        return self._attachments.get(attachment_id)

    async def delete(
        self,
        attachment_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        return self._attachments.pop(attachment_id, None) is not None

    async def list_by_type(
        self,
        content_type: str,
        *,
        limit: int = 50,
        context: ExecutionContext | None = None,
    ) -> list[Attachment]:
        category = classify_content_type(content_type)
        attachments = [
            att
            for att in self._attachments.values()
            if classify_content_type(att.content_type) == category
        ]
        return attachments[:limit]

    async def list_all(
        self,
        *,
        limit: int = 50,
        context: ExecutionContext | None = None,
    ) -> list[Attachment]:
        attachments = list(self._attachments.values())
        return attachments[:limit]

    def get_category(self, content_type: str) -> str:
        return classify_content_type(content_type)

    @property
    def total_attachments(self) -> int:
        return len(self._attachments)
