from __future__ import annotations

import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_ai.models import (
    AICapability,
    CostMetadata,
    ModelMetadata,
    PerformanceMetadata,
    ProviderKind,
    ProviderMetadata,
    ProviderRequest,
    ProviderResponse,
    TokenUsage,
)
from jarvis_ai.provider_sdk import ProviderAdapterBase


class StaticProvider(ProviderAdapterBase):
    def __init__(
        self,
        metadata: ProviderMetadata,
        *,
        response_text: str = "ok",
        stream_chunks: tuple[str, ...] = (),
        fail_invocations: int = 0,
    ) -> None:
        super().__init__(metadata)
        self._response_text = response_text
        self._stream_chunks = stream_chunks
        self._fail_invocations = fail_invocations
        self.invocations = 0

    async def invoke(self, request: ProviderRequest) -> ProviderResponse:
        self.invocations += 1
        if self.invocations <= self._fail_invocations:
            raise RuntimeError(f"provider '{self.metadata.provider_id}' temporary failure")
        return ProviderResponse.create(
            text=f"{self._response_text}:{request.model_id}",
            provider_id=self.metadata.provider_id,
            model_id=request.model_id,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5),
        )

    async def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]:
        if self._stream_chunks:
            for chunk in self._stream_chunks:
                yield ProviderResponse.create(
                    text=chunk,
                    provider_id=self.metadata.provider_id,
                    model_id=request.model_id,
                )
            return
        yield await self.invoke(request)


def build_provider_metadata(
    provider_id: str,
    kind: ProviderKind,
    capabilities: tuple[AICapability, ...],
    supported_models: tuple[str, ...],
    *,
    priority: int = 100,
) -> ProviderMetadata:
    return ProviderMetadata(
        provider_id=provider_id,
        display_name=provider_id.title(),
        kind=kind,
        capabilities=capabilities,
        supported_models=supported_models,
        priority=priority,
    )


def build_model(
    model_id: str,
    provider_id: str,
    capabilities: tuple[AICapability, ...],
    *,
    quality: float = 0.8,
    speed: float = 0.8,
    reliability: float = 0.9,
    input_cost: float = 0.5,
    output_cost: float = 0.8,
    supports_streaming: bool = True,
    tags: frozenset[str] | None = None,
    priority: int = 100,
) -> ModelMetadata:
    return ModelMetadata(
        identifier=model_id,
        provider_id=provider_id,
        capabilities=capabilities,
        context_window=128_000,
        token_limit=4_096,
        supports_streaming=supports_streaming,
        multimodal=False,
        version="1.0",
        available=True,
        cost=CostMetadata(input_per_1k_tokens=input_cost, output_per_1k_tokens=output_cost),
        performance=PerformanceMetadata(
            quality_score=quality,
            speed_score=speed,
            reliability_score=reliability,
        ),
        tags=tags or frozenset(),
        priority=priority,
    )


@pytest.fixture
def conversation_capability() -> tuple[AICapability, ...]:
    return (AICapability.CONVERSATION,)
