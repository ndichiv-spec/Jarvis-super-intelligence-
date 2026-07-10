"""Integration repository contracts."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from jarvis_enterprise.integration.models import (
    IntegrationAdapter,
    IntegrationProvider,
    IntegrationProviderKind,
)


class IntegrationRepository(Protocol):
    def save_provider(self, provider: IntegrationProvider) -> None: ...
    def get_provider(self, provider_id: UUID) -> IntegrationProvider | None: ...
    def list_providers(self, kind: IntegrationProviderKind | None = None) -> list[IntegrationProvider]: ...
    def save_adapter(self, adapter: IntegrationAdapter) -> None: ...
    def get_adapter(self, adapter_id: UUID) -> IntegrationAdapter | None: ...
    def list_adapters(self, org_id: UUID) -> list[IntegrationAdapter]: ...
