"""Integration hub domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class IntegrationProviderKind(StrEnum):
    identity_provider = "identity_provider"
    collaboration = "collaboration"
    ticketing = "ticketing"
    erp = "erp"
    crm = "crm"
    document_management = "document_management"
    monitoring = "monitoring"
    notification = "notification"


class IntegrationStatus(StrEnum):
    configured = "configured"
    active = "active"
    error = "error"
    disconnected = "disconnected"


@dataclass(frozen=True, slots=True)
class IntegrationProvider:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    kind: IntegrationProviderKind = IntegrationProviderKind.collaboration
    version: str = "1.0.0"
    description: str = ""
    adapter_module: str = ""
    config_schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IntegrationAdapter:
    id: UUID = field(default_factory=uuid4)
    provider_id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    name: str = ""
    enabled: bool = True
    status: IntegrationStatus = IntegrationStatus.configured
    configuration: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class IntegrationCapability:
    provider_kind: IntegrationProviderKind = IntegrationProviderKind.collaboration
    capabilities: tuple[str, ...] = ()
    auth_types: tuple[str, ...] = ("oauth2",)
