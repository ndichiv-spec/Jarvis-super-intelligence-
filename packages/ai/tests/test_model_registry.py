from __future__ import annotations

import pytest
from conftest import build_model
from jarvis_ai.model_registry import ModelRegistry, ModelRegistryError
from jarvis_ai.models import AICapability


def test_model_registry_filters_by_provider_and_capability() -> None:
    registry = ModelRegistry()
    registry.register(
        build_model(
            "gpt-4o",
            "openai",
            (AICapability.CONVERSATION, AICapability.REASONING),
        )
    )
    registry.register(
        build_model(
            "text-embedding-3",
            "openai",
            (AICapability.EMBEDDINGS,),
            quality=0.7,
        )
    )

    conversation_models = registry.list_by_capability(AICapability.CONVERSATION)
    assert [model.identifier for model in conversation_models] == ["gpt-4o"]

    openai_models = registry.list_by_provider("openai")
    assert {model.identifier for model in openai_models} == {"gpt-4o", "text-embedding-3"}


def test_model_registry_rejects_duplicate_ids() -> None:
    registry = ModelRegistry()
    model = build_model("gpt-4o", "openai", (AICapability.CONVERSATION,))
    registry.register(model)

    with pytest.raises(ModelRegistryError):
        registry.register(model)
