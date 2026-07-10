from __future__ import annotations

import asyncio

import pytest
from jarvis_infrastructure.adapters.filesystem import (
    AllowAllAuthorizer,
    FileAuthorizationPort,
    LocalFileSystemAdapter,
)
from jarvis_infrastructure.adapters.object_storage import LocalObjectStorageAdapter
from jarvis_infrastructure.adapters.search import InMemorySearchAdapter, SearchDocument
from jarvis_infrastructure.adapters.vector_store import InMemoryVectorStoreAdapter, VectorRecord


class DenyAllAuthorizer(FileAuthorizationPort):
    def is_allowed(self, *, actor_id: str, workspace_id: str, path: str, operation: str) -> bool:
        _ = (actor_id, workspace_id, path, operation)
        return False


def test_in_memory_vector_store_returns_ranked_results() -> None:
    async def _run() -> None:
        adapter = InMemoryVectorStoreAdapter()
        await adapter.start()

        await adapter.upsert(
            (
                VectorRecord(identifier="one", vector=(1.0, 0.0), metadata={"label": "a"}),
                VectorRecord(identifier="two", vector=(0.0, 1.0), metadata={"label": "b"}),
            )
        )

        results = await adapter.search((0.9, 0.1), limit=1)

        assert results[0].identifier == "one"

        await adapter.stop()

    asyncio.run(_run())


def test_in_memory_search_adapter_indexes_and_queries_documents() -> None:
    async def _run() -> None:
        adapter = InMemorySearchAdapter()
        await adapter.start()

        await adapter.index(
            SearchDocument(identifier="doc-1", text="hello infrastructure world", metadata={})
        )
        await adapter.index(SearchDocument(identifier="doc-2", text="goodbye", metadata={}))

        results = await adapter.search("infrastructure", limit=5)

        assert [item.identifier for item in results] == ["doc-1"]

        await adapter.stop()

    asyncio.run(_run())


def test_local_object_storage_adapter_roundtrip(tmp_path) -> None:
    async def _run() -> None:
        adapter = LocalObjectStorageAdapter(root=str(tmp_path / "objects"))
        await adapter.start()

        await adapter.put_object("reports/a.txt", b"payload", content_type="text/plain")

        assert await adapter.get_object("reports/a.txt") == b"payload"
        assert "reports/a.txt" in await adapter.list_objects("reports")

        await adapter.delete_object("reports/a.txt")
        assert "reports/a.txt" not in await adapter.list_objects("reports")

        await adapter.stop()

    asyncio.run(_run())


def test_local_filesystem_adapter_enforces_authorization(tmp_path) -> None:
    async def _run() -> None:
        adapter = LocalFileSystemAdapter(root=str(tmp_path), authorizer=AllowAllAuthorizer())
        await adapter.start()

        await adapter.write(
            actor_id="u1",
            workspace_id="ws1",
            path="docs/readme.txt",
            content=b"hello",
        )
        assert (
            await adapter.read(actor_id="u1", workspace_id="ws1", path="docs/readme.txt")
            == b"hello"
        )

        deny_adapter = LocalFileSystemAdapter(root=str(tmp_path), authorizer=DenyAllAuthorizer())
        await deny_adapter.start()
        with pytest.raises(PermissionError):
            await deny_adapter.read(actor_id="u2", workspace_id="ws1", path="docs/readme.txt")

        await deny_adapter.stop()
        await adapter.stop()

    asyncio.run(_run())
