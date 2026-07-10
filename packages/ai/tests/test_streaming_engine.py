from __future__ import annotations

import asyncio

from conftest import StaticProvider, build_provider_metadata
from jarvis_ai.models import AICapability, ProviderKind, ProviderRequest, StreamEventType
from jarvis_ai.streaming_engine import CancellationToken, StreamingEngine


def test_streaming_engine_emits_token_partial_and_completed_events() -> None:
    provider = StaticProvider(
        build_provider_metadata(
            "openai",
            ProviderKind.OPENAI,
            (AICapability.CONVERSATION,),
            ("gpt-4o",),
        ),
        stream_chunks=("hel", "lo"),
    )
    request = ProviderRequest.create(
        model_id="gpt-4o",
        system_instruction="sys",
        messages=(),
        max_tokens=100,
        temperature=0.2,
    )

    async def collect() -> tuple[StreamEventType, ...]:
        events = [event async for event in StreamingEngine().stream(provider, request)]
        return tuple(event.event_type for event in events)

    event_types = asyncio.run(collect())
    assert event_types[-1] == StreamEventType.COMPLETED
    assert StreamEventType.TOKEN in event_types
    assert StreamEventType.PARTIAL in event_types


def test_streaming_engine_supports_cancellation() -> None:
    provider = StaticProvider(
        build_provider_metadata(
            "openai",
            ProviderKind.OPENAI,
            (AICapability.CONVERSATION,),
            ("gpt-4o",),
        ),
        stream_chunks=("a", "b", "c"),
    )
    request = ProviderRequest.create(
        model_id="gpt-4o",
        system_instruction="sys",
        messages=(),
        max_tokens=100,
        temperature=0.2,
    )
    cancellation = CancellationToken()

    async def collect() -> tuple[StreamEventType, ...]:
        event_types: list[StreamEventType] = []
        async for event in StreamingEngine().stream(provider, request, cancellation):
            event_types.append(event.event_type)
            if event.event_type == StreamEventType.TOKEN:
                cancellation.cancel()
        return tuple(event_types)

    event_types = asyncio.run(collect())
    assert StreamEventType.CANCELLED in event_types
