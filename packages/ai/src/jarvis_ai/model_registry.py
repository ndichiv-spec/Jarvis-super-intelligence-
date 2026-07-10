from __future__ import annotations

from jarvis_ai.models import AICapability, ModelMetadata


class ModelRegistryError(ValueError):
    pass


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, ModelMetadata] = {}

    def register(self, model: ModelMetadata) -> None:
        if model.identifier in self._models:
            raise ModelRegistryError(f"Model '{model.identifier}' is already registered.")
        if model.context_window <= 0 or model.token_limit <= 0:
            raise ModelRegistryError("Model context and token limits must be greater than zero.")
        self._models[model.identifier] = model

    def get(self, model_id: str) -> ModelMetadata:
        model = self._models.get(model_id)
        if model is None:
            raise ModelRegistryError(f"Model '{model_id}' is not registered.")
        return model

    def list(
        self,
        *,
        provider_id: str | None = None,
        capability: AICapability | None = None,
        streaming: bool | None = None,
        available_only: bool = True,
    ) -> tuple[ModelMetadata, ...]:
        models = tuple(self._models.values())
        if available_only:
            models = tuple(model for model in models if model.available)
        if provider_id is not None:
            models = tuple(model for model in models if model.provider_id == provider_id)
        if capability is not None:
            models = tuple(model for model in models if capability in model.capabilities)
        if streaming is not None:
            models = tuple(model for model in models if model.supports_streaming is streaming)

        return tuple(
            sorted(
                models,
                key=lambda model: (
                    model.priority,
                    -model.performance.quality_score,
                    -model.performance.reliability_score,
                ),
            )
        )

    def list_by_provider(self, provider_id: str) -> tuple[ModelMetadata, ...]:
        return self.list(provider_id=provider_id)

    def list_by_capability(self, capability: AICapability) -> tuple[ModelMetadata, ...]:
        return self.list(capability=capability)
