from __future__ import annotations

from jarvis_ai.models import AICapability, ModelMetadata, ProviderMetadata


class CapabilityRegistry:
    def __init__(self) -> None:
        self._provider_index: dict[AICapability, set[str]] = {}
        self._model_index: dict[AICapability, set[str]] = {}

    def register_provider(self, provider: ProviderMetadata) -> None:
        for capability in provider.capabilities:
            self._provider_index.setdefault(capability, set()).add(provider.provider_id)

    def register_model(self, model: ModelMetadata) -> None:
        for capability in model.capabilities:
            self._model_index.setdefault(capability, set()).add(model.identifier)

    def providers_for(self, capability: AICapability) -> tuple[str, ...]:
        return tuple(sorted(self._provider_index.get(capability, set())))

    def models_for(self, capability: AICapability) -> tuple[str, ...]:
        return tuple(sorted(self._model_index.get(capability, set())))

    def available_capabilities(self) -> tuple[AICapability, ...]:
        capabilities = set(self._provider_index) | set(self._model_index)
        return tuple(sorted(capabilities, key=lambda capability: capability.value))
