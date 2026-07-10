from __future__ import annotations

import pytest
from jarvis_ai.models import AICapability
from jarvis_ai.provider_registry import ProviderRegistry, ProviderRegistryError
from jarvis_ai.provider_sdk import OpenAIAdapter


def test_provider_registry_registers_and_discovers_capabilities() -> None:
    provider = OpenAIAdapter(("gpt-4o",), (AICapability.CONVERSATION, AICapability.SUMMARIZATION))
    registry = ProviderRegistry()

    registry.register(provider)

    discovered = registry.discover_capabilities()
    assert discovered[AICapability.CONVERSATION] == ("openai",)
    assert discovered[AICapability.SUMMARIZATION] == ("openai",)


def test_provider_registry_rejects_duplicate_registration() -> None:
    provider = OpenAIAdapter(("gpt-4o",), (AICapability.CONVERSATION,))
    registry = ProviderRegistry()

    registry.register(provider)

    with pytest.raises(ProviderRegistryError):
        registry.register(provider)
