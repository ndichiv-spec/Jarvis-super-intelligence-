"""Enterprise integration hub service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.integration.models import (
    IntegrationAdapter,
    IntegrationCapability,
    IntegrationProvider,
    IntegrationProviderKind,
    IntegrationStatus,
)
from jarvis_enterprise.integration.repository import IntegrationRepository


class IntegrationHubService:
    def __init__(self, repository: IntegrationRepository) -> None:
        self._repository = repository

    def register_provider(
        self, name: str, kind: IntegrationProviderKind,
        adapter_module: str = "", description: str = "",
    ) -> IntegrationProvider:
        provider = IntegrationProvider(name=name, kind=kind, adapter_module=adapter_module, description=description)
        self._repository.save_provider(provider)
        return provider

    def list_providers(self, kind: IntegrationProviderKind | None = None) -> list[IntegrationProvider]:
        return self._repository.list_providers(kind)

    def configure_adapter(
        self, provider_id: UUID, org_id: UUID, name: str,
        configuration: dict | None = None,
    ) -> IntegrationAdapter | None:
        provider = self._repository.get_provider(provider_id)
        if provider is None:
            return None
        adapter = IntegrationAdapter(
            provider_id=provider_id, org_id=org_id, name=name,
            configuration=configuration or {},
        )
        self._repository.save_adapter(adapter)
        return adapter

    def enable_adapter(self, adapter_id: UUID) -> IntegrationAdapter | None:
        adapter = self._repository.get_adapter(adapter_id)
        if adapter is None:
            return None
        updated = IntegrationAdapter(
            id=adapter.id, provider_id=adapter.provider_id, org_id=adapter.org_id,
            name=adapter.name, enabled=True, status=IntegrationStatus.active,
            configuration=adapter.configuration, created_at=adapter.created_at,
        )
        self._repository.save_adapter(updated)
        return updated

    def disable_adapter(self, adapter_id: UUID) -> IntegrationAdapter | None:
        adapter = self._repository.get_adapter(adapter_id)
        if adapter is None:
            return None
        updated = IntegrationAdapter(
            id=adapter.id, provider_id=adapter.provider_id, org_id=adapter.org_id,
            name=adapter.name, enabled=False, status=IntegrationStatus.disconnected,
            configuration=adapter.configuration, created_at=adapter.created_at,
        )
        self._repository.save_adapter(updated)
        return updated

    def list_adapters(self, org_id: UUID) -> list[IntegrationAdapter]:
        return self._repository.list_adapters(org_id)

    def get_capabilities(self, kind: IntegrationProviderKind) -> IntegrationCapability:
        caps = {
            IntegrationProviderKind.identity_provider: ("user_provisioning", "sso", "group_sync"),
            IntegrationProviderKind.collaboration: ("messaging", "file_sharing", "presence"),
            IntegrationProviderKind.ticketing: ("issue_tracking", "workflow", "sla"),
            IntegrationProviderKind.erp: ("inventory", "finance", "hr"),
            IntegrationProviderKind.crm: ("contacts", "deals", "interactions"),
            IntegrationProviderKind.document_management: ("storage", "versioning", "collaboration"),
            IntegrationProviderKind.monitoring: ("alerts", "logs", "metrics"),
            IntegrationProviderKind.notification: ("push", "email", "webhook"),
        }
        return IntegrationCapability(
            provider_kind=kind,
            capabilities=caps.get(kind, ()),
            auth_types=("oauth2", "api_key", "basic"),
        )
