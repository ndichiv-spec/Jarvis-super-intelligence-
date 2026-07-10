"""Resource management domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ResourceType(StrEnum):
    compute = "compute"
    storage = "storage"
    ai_provider = "ai_provider"
    extension = "extension"
    memory = "memory"
    bandwidth = "bandwidth"


class QuotaPeriod(StrEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    unlimited = "unlimited"


@dataclass(frozen=True, slots=True)
class Quota:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    resource_type: ResourceType = ResourceType.compute
    resource_name: str = ""
    limit: int = 0
    used: int = 0
    period: QuotaPeriod = QuotaPeriod.monthly


@dataclass(frozen=True, slots=True)
class ResourceUsage:
    org_id: UUID = field(default_factory=uuid4)
    workspace_id: UUID = field(default_factory=uuid4)
    resource_type: ResourceType = ResourceType.compute
    resource_name: str = ""
    amount: int = 0
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class UsagePolicy:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    resource_type: ResourceType = ResourceType.compute
    max_per_org: int = 0
    max_per_workspace: int = 0
    notify_at_pct: int = 80
    enabled: bool = True


@dataclass(frozen=True, slots=True)
class ComputeAllocation:
    workspace_id: UUID = field(default_factory=uuid4)
    cpu_cores: int = 0
    memory_gb: int = 0
    gpu_count: int = 0


@dataclass(frozen=True, slots=True)
class StorageAllocation:
    workspace_id: UUID = field(default_factory=uuid4)
    storage_gb: int = 0
    used_gb: int = 0
