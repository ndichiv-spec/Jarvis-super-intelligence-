"""Tests for Enterprise Integration Hub."""

from uuid import uuid4

from jarvis_enterprise.integration.models import (
    IntegrationAdapter,
    IntegrationCapability,
    IntegrationProvider,
    IntegrationProviderKind,
    IntegrationStatus,
)
from jarvis_enterprise.integration.repository import IntegrationRepository
from jarvis_enterprise.integration.service import IntegrationHubService


class InMemoryIntegrationRepo:
    def __init__(self):
        self._providers: dict = {}
        self._adapters: dict = {}

    def save_provider(self, provider) -> None:
        self._providers[provider.id] = provider

    def get_provider(self, provider_id) -> IntegrationProvider | None:
        return self._providers.get(provider_id)

    def list_providers(self, kind=None) -> list[IntegrationProvider]:
        if kind:
            return [p for p in self._providers.values() if p.kind == kind]
        return list(self._providers.values())

    def save_adapter(self, adapter) -> None:
        self._adapters[adapter.id] = adapter

    def get_adapter(self, adapter_id) -> IntegrationAdapter | None:
        return self._adapters.get(adapter_id)

    def list_adapters(self, org_id) -> list[IntegrationAdapter]:
        return [a for a in self._adapters.values() if a.org_id == org_id]


class TestIntegrationService:
    def setup_method(self):
        self.repo = IntegrationHubService(InMemoryIntegrationRepo())

    def test_register_provider(self):
        provider = self.repo.register_provider("Slack", IntegrationProviderKind.collaboration)
        assert provider.name == "Slack"
        assert provider.kind == IntegrationProviderKind.collaboration

    def test_list_providers(self):
        self.repo.register_provider("Slack", IntegrationProviderKind.collaboration)
        self.repo.register_provider("Okta", IntegrationProviderKind.identity_provider)
        assert len(self.repo.list_providers()) == 2
        assert len(self.repo.list_providers(IntegrationProviderKind.collaboration)) == 1

    def test_configure_adapter(self):
        provider = self.repo.register_provider("Jira", IntegrationProviderKind.ticketing)
        adapter = self.repo.configure_adapter(provider.id, uuid4(), "My Jira", {"url": "https://jira.example.com"})
        assert adapter is not None
        assert adapter.name == "My Jira"

    def test_configure_adapter_nonexistent_provider(self):
        adapter = self.repo.configure_adapter(uuid4(), uuid4(), "Test")
        assert adapter is None

    def test_enable_adapter(self):
        provider = self.repo.register_provider("Slack", IntegrationProviderKind.collaboration)
        adapter = self.repo.configure_adapter(provider.id, uuid4(), "Slack WS")
        enabled = self.repo.enable_adapter(adapter.id)
        assert enabled is not None
        assert enabled.enabled is True

    def test_disable_adapter(self):
        provider = self.repo.register_provider("Slack", IntegrationProviderKind.collaboration)
        adapter = self.repo.configure_adapter(provider.id, uuid4(), "Slack WS")
        disabled = self.repo.disable_adapter(adapter.id)
        assert disabled is not None
        assert disabled.enabled is False

    def test_get_capabilities(self):
        caps = self.repo.get_capabilities(IntegrationProviderKind.ticketing)
        assert "issue_tracking" in caps.capabilities
        assert "oauth2" in caps.auth_types
