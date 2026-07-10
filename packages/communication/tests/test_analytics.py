from __future__ import annotations

import pytest

from jarvis_communication.analytics import AnalyticsEngine
from jarvis_communication.context import ExecutionContext


@pytest.fixture
def engine() -> AnalyticsEngine:
    return AnalyticsEngine()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_track_and_query(engine: AnalyticsEngine, context: ExecutionContext) -> None:
    await engine.track("message.sent", {"channel": "internal"}, source="test", context=context)
    await engine.track("message.sent", {"channel": "email"}, source="test", context=context)
    await engine.track("notification.sent", {"level": "info"}, source="test", context=context)
    results = await engine.query(event_type="message.sent", context=context)
    assert len(results) == 2
    all_events = await engine.query(context=context)
    assert len(all_events) == 3


@pytest.mark.asyncio
async def test_get_event_counts(engine: AnalyticsEngine, context: ExecutionContext) -> None:
    await engine.track("message.sent", {}, context=context)
    await engine.track("message.sent", {}, context=context)
    await engine.track("notification.sent", {}, context=context)
    counts = await engine.get_event_counts(context=context)
    assert counts["message.sent"] == 2
    assert counts["notification.sent"] == 1


@pytest.mark.asyncio
async def test_get_source_counts(engine: AnalyticsEngine, context: ExecutionContext) -> None:
    await engine.track("event.a", {}, source="src1", context=context)
    await engine.track("event.b", {}, source="src1", context=context)
    await engine.track("event.c", {}, source="src2", context=context)
    counts = await engine.get_source_counts(context=context)
    assert counts["src1"] == 2
    assert counts["src2"] == 1


@pytest.mark.asyncio
async def test_get_message_statistics(engine: AnalyticsEngine, context: ExecutionContext) -> None:
    await engine.track("message.sent", {}, context=context)
    await engine.track("notification.sent", {}, context=context)
    stats = await engine.get_message_statistics(context=context)
    assert stats["total_messages"] == 1


@pytest.mark.asyncio
async def test_get_response_latency(engine: AnalyticsEngine, context: ExecutionContext) -> None:
    await engine.track("response.latency", {"value_ms": 42.5}, context=context)
    await engine.track("response.latency", {"value_ms": 100.0}, context=context)
    latency = await engine.get_response_latency(context=context)
    assert latency["count"] == 2
    assert latency["avg_ms"] == 71.25
    assert latency["min_ms"] == 42.5
    assert latency["max_ms"] == 100.0
