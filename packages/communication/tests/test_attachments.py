from __future__ import annotations

import pytest

from jarvis_communication.attachments import SUPPORTED_TYPES, AttachmentManager, classify_content_type
from jarvis_communication.context import ExecutionContext


@pytest.fixture
def manager() -> AttachmentManager:
    return AttachmentManager()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


def test_classify_content_type() -> None:
    assert classify_content_type("application/pdf") == "pdf"
    assert classify_content_type("image/png") == "image"
    assert classify_content_type("audio/mpeg") == "audio"
    assert classify_content_type("video/mp4") == "video"
    assert classify_content_type("text/x-python") == "code"
    assert classify_content_type("application/zip") == "archive"
    assert classify_content_type("application/unknown") == "other"


@pytest.mark.asyncio
async def test_store_and_get(manager: AttachmentManager, context: ExecutionContext) -> None:
    att = await manager.store("test.pdf", "application/pdf", 1024, "/storage/test.pdf", context=context)
    retrieved = await manager.get(att.attachment_id, context=context)
    assert retrieved is not None
    assert retrieved.filename == "test.pdf"
    assert retrieved.size == 1024


@pytest.mark.asyncio
async def test_delete(manager: AttachmentManager, context: ExecutionContext) -> None:
    att = await manager.store("del.txt", "text/plain", 100, "/storage/del.txt", context=context)
    assert await manager.delete(att.attachment_id, context=context) is True
    assert await manager.get(att.attachment_id, context=context) is None


@pytest.mark.asyncio
async def test_list_by_type(manager: AttachmentManager, context: ExecutionContext) -> None:
    await manager.store("doc.pdf", "application/pdf", 100, "/path", context=context)
    await manager.store("img.png", "image/png", 200, "/path", context=context)
    await manager.store("doc2.pdf", "application/pdf", 300, "/path", context=context)
    pdfs = await manager.list_by_type("application/pdf", context=context)
    assert len(pdfs) == 2
    images = await manager.list_by_type("image/png", context=context)
    assert len(images) == 1
