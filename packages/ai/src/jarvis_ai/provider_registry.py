from __future__ import annotations

from jarvis_ai.interfaces import ProviderAdapter
from jarvis_ai.models import AICapability


class ProviderRegistryError(ValueError):
    pass


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ProviderAdapter] = {}

    def register(self, provider: ProviderAdapter) -> None:
        provider_id = provider.metadata.provider_id
        if provider_id in self._providers:
            raise ProviderRegistryError(f"Provider '{provider_id}' is already registered.")
        self._providers[provider_id] = provider

    def unregister(self, provider_id: str) -> ProviderAdapter:
        if provider_id not in self._providers:
            raise ProviderRegistryError(f"Provider '{provider_id}' is not registered.")
        return self._providers.pop(provider_id)

    def get(self, provider_id: str) -> ProviderAdapter:
        provider = self._providers.get(provider_id)
        if provider is None:
            raise ProviderRegistryError(f"Provider '{provider_id}' is not registered.")
        return provider

    def has(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def list_all(self) -> tuple[ProviderAdapter, ...]:
        return tuple(self._providers.values())

    def list_available(
        self,
        capability: AICapability | None = None,
    ) -> tuple[ProviderAdapter, ...]:
        providers = tuple(
            provider for provider in self._providers.values() if provider.metadata.available
        )
        if capability is None:
            return providers
        return tuple(
            provider for provider in providers if capability in provider.metadata.capabilities
        )

    def discover_capabilities(self) -> dict[AICapability, tuple[str, ...]]:
        index: dict[AICapability, list[str]] = {}
        for provider in self._providers.values():
            if not provider.metadata.available:
                continue
            for capability in provider.metadata.capabilities:
                index.setdefault(capability, []).append(provider.metadata.provider_id)

        return {
            capability: tuple(sorted(provider_ids)) for capability, provider_ids in index.items()
        }
