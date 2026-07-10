from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import timedelta

import pytest
from jarvis_ai.models import Message, ProviderRequest, ProviderResponse
from jarvis_infrastructure.adapters.ai import OpenAIProviderAdapter
from jarvis_infrastructure.adapters.logging import ConsoleLoggerAdapter
from jarvis_infrastructure.adapters.messaging import (
    EventMessage,
    ExecutionContext,
    InMemoryDeadLetterSink,
    InMemoryEventStoreAdapter,
)
from jarvis_infrastructure.adapters.metrics import InMemoryMetricsAdapter
from jarvis_infrastructure.adapters.secrets import (
    EnvironmentSecretProviderAdapter,
    FileSecretProviderAdapter,
)


class FakeAIClient:
    async def supports_model(self, model_id: str) -> bool:
        return model_id == "test-model"

    async def invoke(self, request: ProviderRequest) -> ProviderResponse:
        _ = request
        return ProviderResponse.create(
            text="ok",
            provider_id="ai.openai",
            model_id="test-model",
        )

    def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]:
        _ = request

        async def _iterator() -> AsyncIterator[ProviderResponse]:
            yield ProviderResponse.create(
                text="chunk",
                provider_id="ai.openai",
                model_id="test-model",
            )

        return _iterator()


class _LoggerContext:
    correlation_id = "test-correlation"
    execution_id = "test-execution"
    source = "test"


def _execution_context() -> ExecutionContext:
    if hasattr(ExecutionContext, "new"):
        return ExecutionContext.new(source="test")  # type: ignore[call-arg]
    return ExecutionContext(correlation_id="test-correlation")


def test_event_store_and_dead_letter_adapters() -> None:
    async def _run() -> None:
        event_store = InMemoryEventStoreAdapter()
        dead_letter = InMemoryDeadLetterSink()
        context = _LoggerContext()

        await event_store.start()
        await dead_letter.start()

        event = EventMessage(message_name="test.event", payload={"ok": True})
        version = await event_store.append(event)

        assert version == 1
        replayed = [record async for record in event_store.replay(event_name="test.event")]
        assert len(replayed) == 1

        await dead_letter.publish_dead_letter(event, context, RuntimeError("boom"))
        assert len(await dead_letter.records()) == 1

        await dead_letter.stop()
        await event_store.stop()

    asyncio.run(_run())


def test_metrics_and_logger_adapters() -> None:
    async def _run() -> None:
        metrics = InMemoryMetricsAdapter()
        logger = ConsoleLoggerAdapter()
        context = _LoggerContext()

        await metrics.start()
        await logger.start()

        metrics.increment("requests_total", tags={"endpoint": "chat"})
        metrics.timing("request_duration", timedelta(milliseconds=42), tags={"endpoint": "chat"})
        logger.info("request completed", context=context)

        assert metrics.counters()["requests_total|endpoint=chat"] == 1
        assert metrics.timings()["request_duration|endpoint=chat"][0] == 42.0

        await logger.stop()
        await metrics.stop()

    asyncio.run(_run())


def test_openai_provider_adapter_with_fake_client() -> None:
    async def _run() -> None:
        adapter = OpenAIProviderAdapter(client=FakeAIClient())
        await adapter.start()

        request = ProviderRequest.create(
            model_id="test-model",
            system_instruction="You are a test model",
            messages=(Message(role="user", content="hello"),),
            max_tokens=64,
            temperature=0.2,
        )

        assert await adapter.supports_model("test-model") is True
        response = await adapter.invoke(request)
        chunks = [chunk async for chunk in adapter.stream(request)]

        assert response.text == "ok"
        assert chunks[0].text == "chunk"

        await adapter.stop()

    asyncio.run(_run())


def test_secret_provider_adapters(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    async def _run() -> None:
        monkeypatch.setenv("JARVIS_SECRET_API_KEY", "secret")
        env_adapter = EnvironmentSecretProviderAdapter(prefix="JARVIS_SECRET_")
        await env_adapter.start()
        assert await env_adapter.resolve("api_key") == "secret"
        await env_adapter.stop()

        secrets_file = tmp_path / "secrets.json"
        secrets_file.write_text('{"token":"abc"}', encoding="utf-8")
        file_adapter = FileSecretProviderAdapter(file_path=str(secrets_file))
        await file_adapter.start()
        assert await file_adapter.resolve("token") == "abc"
        await file_adapter.stop()

    asyncio.run(_run())
