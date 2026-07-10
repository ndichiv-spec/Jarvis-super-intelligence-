from __future__ import annotations

from collections.abc import AsyncIterator

from jarvis_ai.models import (
    AICapability,
    ProviderKind,
    ProviderMetadata,
    ProviderRequest,
    ProviderResponse,
)


class ProviderAdapterError(RuntimeError):
    pass


class ProviderAdapterBase:
    def __init__(self, metadata: ProviderMetadata) -> None:
        self._metadata = metadata
        self._supported_models = frozenset(metadata.supported_models)

    @property
    def metadata(self) -> ProviderMetadata:
        return self._metadata

    async def supports_model(self, model_id: str) -> bool:
        return model_id in self._supported_models

    async def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]:
        yield await self.invoke(request)

    async def invoke(self, request: ProviderRequest) -> ProviderResponse:
        raise ProviderAdapterError(
            f"Provider '{self._metadata.provider_id}' has no live integration configured for model "
            f"'{request.model_id}'."
        )


class OpenAIAdapter(ProviderAdapterBase):
    def __init__(
        self,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id="openai",
                display_name="OpenAI",
                kind=ProviderKind.OPENAI,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )


class AnthropicAdapter(ProviderAdapterBase):
    def __init__(
        self,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id="anthropic",
                display_name="Anthropic",
                kind=ProviderKind.ANTHROPIC,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )


class GoogleAdapter(ProviderAdapterBase):
    def __init__(
        self,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id="google",
                display_name="Google",
                kind=ProviderKind.GOOGLE,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )


class OllamaAdapter(ProviderAdapterBase):
    def __init__(
        self,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id="ollama",
                display_name="Ollama",
                kind=ProviderKind.OLLAMA,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )


class VLLMAdapter(ProviderAdapterBase):
    def __init__(
        self,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id="vllm",
                display_name="vLLM",
                kind=ProviderKind.VLLM,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )


class LocalModelsAdapter(ProviderAdapterBase):
    def __init__(
        self,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id="local",
                display_name="Local Models",
                kind=ProviderKind.LOCAL,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )


class FutureProviderAdapter(ProviderAdapterBase):
    def __init__(
        self,
        provider_id: str,
        display_name: str,
        supported_models: tuple[str, ...],
        capabilities: tuple[AICapability, ...],
    ) -> None:
        super().__init__(
            ProviderMetadata(
                provider_id=provider_id,
                display_name=display_name,
                kind=ProviderKind.FUTURE,
                capabilities=capabilities,
                supported_models=supported_models,
            )
        )
