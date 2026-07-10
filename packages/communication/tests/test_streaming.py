from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.streaming import StreamingEngine


@pytest.fixture
def engine() -> StreamingEngine:
    return StreamingEngine()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_start_and_end_stream(engine: StreamingEngine, context: ExecutionContext) -> None:
    stream_id = await engine.start_stream("test-stream", context=context)
    assert stream_id == "test-stream"
    assert engine.active_stream_count == 1
    await engine.end_stream("test-stream", context=context)
    assert engine.active_stream_count == 0


@pytest.mark.asyncio
async def test_push_chunk(engine: StreamingEngine, context: ExecutionContext) -> None:
    await engine.start_stream("stream-1", context=context)
    chunk = await engine.push_chunk("stream-1", "Hello", context=context)
    assert chunk.sequence == 0
    assert chunk.data == "Hello"
    chunk2 = await engine.push_chunk("stream-1", "World", context=context)
    assert chunk2.sequence == 1
    assert chunk2.data == "World"


@pytest.mark.asyncio
async def test_get_stream_chunks(engine: StreamingEngine, context: ExecutionContext) -> None:
    await engine.start_stream("stream-2", context=context)
    await engine.push_chunk("stream-2", "A", context=context)
    await engine.push_chunk("stream-2", "B", context=context)
    chunks = await engine.get_stream_chunks("stream-2", context=context)
    assert len(chunks) == 2
    assert [c.data for c in chunks] == ["A", "B"]


@pytest.mark.asyncio
async def test_push_to_nonexistent_stream(engine: StreamingEngine, context: ExecutionContext) -> None:
    with pytest.raises(ValueError, match="not found"):
        await engine.push_chunk("nonexistent", "data", context=context)


@pytest.mark.asyncio
async def test_get_active_streams(engine: StreamingEngine, context: ExecutionContext) -> None:
    await engine.start_stream("s1", context=context)
    await engine.start_stream("s2", context=context)
    active = engine.get_active_streams()
    assert "s1" in active
    assert "s2" in active


@pytest.mark.asyncio
async def test_subscribe(engine: StreamingEngine, context: ExecutionContext) -> None:
    await engine.start_stream("sub-stream", context=context)
    chunks: list[str] = []

    async def collect():
        async for chunk in engine.subscribe("sub-stream", context=context):
            chunks.append(chunk)
            if len(chunks) >= 2:
                break

    import asyncio
    task = asyncio.create_task(collect())
    await asyncio.sleep(0.05)
    await engine.push_chunk("sub-stream", "First", context=context)
    await asyncio.sleep(0.05)
    await engine.push_chunk("sub-stream", "Second", context=context)
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, StopAsyncIteration):
        pass
    assert len(chunks) >= 1
