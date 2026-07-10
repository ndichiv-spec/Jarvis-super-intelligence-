from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import StreamChunk


class StreamingEngine:
    def __init__(self) -> None:
        self._streams: dict[str, list[StreamChunk]] = {}
        self._subscribers: dict[str, list[Any]] = {}

    async def start_stream(
        self,
        stream_id: str,
        *,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> str:
        self._streams[stream_id] = []
        self._subscribers[stream_id] = []
        return stream_id

    async def push_chunk(
        self,
        stream_id: str,
        data: str,
        *,
        chunk_type: str = "data",
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> StreamChunk:
        if stream_id not in self._streams:
            raise ValueError(f"Stream '{stream_id}' not found")
        sequence = len(self._streams[stream_id])
        chunk = StreamChunk(
            stream_id=stream_id,
            sequence=sequence,
            data=data,
            chunk_type=chunk_type,
            metadata=metadata or {},
        )
        self._streams[stream_id].append(chunk)
        for queue in self._subscribers.get(stream_id, []):
            try:
                queue.append(chunk)
            except Exception:
                pass
        return chunk

    async def end_stream(
        self,
        stream_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        if stream_id in self._streams:
            del self._streams[stream_id]
        if stream_id in self._subscribers:
            del self._subscribers[stream_id]

    async def subscribe(
        self,
        stream_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> AsyncIterator[str]:
        if stream_id not in self._streams:
            return
        queue: list[StreamChunk] = []
        self._subscribers.setdefault(stream_id, []).append(queue)
        try:
            while True:
                while queue:
                    chunk = queue.pop(0)
                    yield chunk.data
                    if chunk.chunk_type == "end":
                        return
                import asyncio
                await asyncio.sleep(0.01)
        finally:
            if stream_id in self._subscribers:
                if queue in self._subscribers[stream_id]:
                    self._subscribers[stream_id].remove(queue)

    async def get_stream_chunks(
        self,
        stream_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[StreamChunk]:
        return self._streams.get(stream_id, [])

    async def stream_ai_response(
        self,
        stream_id: str,
        response_generator: AsyncIterator[str],
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        await self.start_stream(stream_id, context=context)
        try:
            async for chunk_data in response_generator:
                await self.push_chunk(stream_id, chunk_data, context=context)
        finally:
            await self.push_chunk(stream_id, "", chunk_type="end", context=context)

    async def stream_agent_execution(
        self,
        stream_id: str,
        updates: AsyncIterator[str],
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        await self.start_stream(stream_id, context=context)
        try:
            async for update in updates:
                await self.push_chunk(
                    stream_id, update, chunk_type="agent_update", context=context
                )
        finally:
            await self.push_chunk(stream_id, "", chunk_type="end", context=context)

    async def stream_planning_progress(
        self,
        stream_id: str,
        progress: AsyncIterator[str],
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        await self.start_stream(stream_id, context=context)
        try:
            async for update in progress:
                await self.push_chunk(
                    stream_id, update, chunk_type="planning_progress", context=context
                )
        finally:
            await self.push_chunk(stream_id, "", chunk_type="end", context=context)

    def get_active_streams(self) -> list[str]:
        return list(self._streams.keys())

    @property
    def active_stream_count(self) -> int:
        return len(self._streams)
