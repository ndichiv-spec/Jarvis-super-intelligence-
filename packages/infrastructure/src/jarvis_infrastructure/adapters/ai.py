from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from jarvis_ai.interfaces import ProviderAdapter
from jarvis_ai.models import (
    AICapability,
    ProviderKind,
    ProviderMetadata,
    ProviderRequest,
    ProviderResponse,
)

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


class AIProviderClient(Protocol):
    async def supports_model(self, model_id: str) -> bool: ...

    async def invoke(self, request: ProviderRequest) -> ProviderResponse: ...

    def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]: ...


class _ProviderAdapter(BaseInfrastructureAdapter, ProviderAdapter):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        kind: ProviderKind,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
        client: AIProviderClient | None,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("ai-provider", "inference", "streaming"),
                configuration_profile="default",
                compatibility=("provider-adapter:v1",),
            )
        )
        self._provider_metadata = ProviderMetadata(
            provider_id=identifier,
            display_name=provider.title(),
            kind=kind,
            capabilities=capabilities,
            supported_models=supported_models,
        )
        self._client = client

    @property
    def metadata(self) -> ProviderMetadata:
        return self._provider_metadata

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError(f"{self.adapter_metadata.provider} AI client is required.")
        await super().start()

    async def supports_model(self, model_id: str) -> bool:
        if model_id in self._provider_metadata.supported_models:
            return True
        if self._client is None:
            return False
        return await self._client.supports_model(model_id)

    async def invoke(self, request: ProviderRequest) -> ProviderResponse:
        if self._client is None:
            raise RuntimeError("AI provider client is not configured.")
        return await self._client.invoke(request)

    def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]:
        if self._client is None:
            raise RuntimeError("AI provider client is not configured.")
        return self._client.stream(request)


class OpenAIProviderAdapter(_ProviderAdapter):
    def __init__(self, *, client: AIProviderClient | None = None) -> None:
        super().__init__(
            identifier="ai.openai",
            provider="openai",
            kind=ProviderKind.OPENAI,
            supported_models=("gpt-4.1", "gpt-4o", "gpt-4o-mini"),
            capabilities=(
                AICapability.CONVERSATION,
                AICapability.REASONING,
                AICapability.TOOL_CALLING,
            ),
            client=client,
        )


class AnthropicProviderAdapter(_ProviderAdapter):
    def __init__(self, *, client: AIProviderClient | None = None) -> None:
        super().__init__(
            identifier="ai.anthropic",
            provider="anthropic",
            kind=ProviderKind.ANTHROPIC,
            supported_models=("claude-3-7-sonnet", "claude-3-5-haiku"),
            capabilities=(
                AICapability.CONVERSATION,
                AICapability.REASONING,
                AICapability.SUMMARIZATION,
            ),
            client=client,
        )


class GoogleProviderAdapter(_ProviderAdapter):
    def __init__(self, *, client: AIProviderClient | None = None) -> None:
        super().__init__(
            identifier="ai.google",
            provider="google",
            kind=ProviderKind.GOOGLE,
            supported_models=("gemini-2.0-flash", "gemini-1.5-pro"),
            capabilities=(
                AICapability.CONVERSATION,
                AICapability.VISION,
                AICapability.STRUCTURED_OUTPUT,
            ),
            client=client,
        )


class OllamaProviderAdapter(_ProviderAdapter):
    def __init__(self, *, client: AIProviderClient | None = None) -> None:
        super().__init__(
            identifier="ai.ollama",
            provider="ollama",
            kind=ProviderKind.OLLAMA,
            supported_models=("llama3.1", "mistral", "qwen2.5"),
            capabilities=(
                AICapability.CONVERSATION,
                AICapability.CODE_GENERATION,
                AICapability.TOOL_CALLING,
            ),
            client=client,
        )


class VllmProviderAdapter(_ProviderAdapter):
    def __init__(self, *, client: AIProviderClient | None = None) -> None:
        super().__init__(
            identifier="ai.vllm",
            provider="vllm",
            kind=ProviderKind.VLLM,
            supported_models=("meta-llama/Meta-Llama-3-8B-Instruct",),
            capabilities=(
                AICapability.CONVERSATION,
                AICapability.REASONING,
                AICapability.CODE_GENERATION,
            ),
            client=client,
        )
