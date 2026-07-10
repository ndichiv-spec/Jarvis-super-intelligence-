"""Resource management service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.resource_management.models import (
    ComputeAllocation,
    Quota,
    QuotaPeriod,
    ResourceType,
    ResourceUsage,
    StorageAllocation,
    UsagePolicy,
)
from jarvis_enterprise.resource_management.repository import ResourceRepository


class ResourceManagementService:
    def __init__(self, repository: ResourceRepository) -> None:
        self._repository = repository

    def set_quota(
        self, org_id: UUID, resource_type: ResourceType,
        resource_name: str, limit: int,
        period: QuotaPeriod = QuotaPeriod.monthly,
    ) -> Quota:
        quota = Quota(org_id=org_id, resource_type=resource_type, resource_name=resource_name, limit=limit, period=period)
        self._repository.save_quota(quota)
        return quota

    def get_quota(self, org_id: UUID, resource_type: str, resource_name: str) -> Quota | None:
        return self._repository.get_quota(org_id, resource_type, resource_name)

    def list_quotas(self, org_id: UUID) -> list[Quota]:
        return self._repository.list_quotas(org_id)

    def record_usage(self, org_id: UUID, workspace_id: UUID, resource_type: ResourceType, resource_name: str, amount: int) -> ResourceUsage:
        usage = ResourceUsage(org_id=org_id, workspace_id=workspace_id, resource_type=resource_type, resource_name=resource_name, amount=amount)
        self._repository.record_usage(usage)
        return usage

    def check_quota(self, org_id: UUID, resource_type: str, resource_name: str) -> tuple[bool, int]:
        quota = self._repository.get_quota(org_id, resource_type, resource_name)
        if quota is None:
            return True, 0
        remaining = quota.limit - quota.used
        return remaining > 0, remaining

    def create_usage_policy(
        self, name: str, resource_type: ResourceType,
        max_per_org: int = 0, max_per_workspace: int = 0,
    ) -> UsagePolicy:
        policy = UsagePolicy(name=name, resource_type=resource_type, max_per_org=max_per_org, max_per_workspace=max_per_workspace)
        self._repository.save_usage_policy(policy)
        return policy

    def set_compute_allocation(self, workspace_id: UUID, cpu_cores: int, memory_gb: int, gpu_count: int = 0) -> ComputeAllocation:
        alloc = ComputeAllocation(workspace_id=workspace_id, cpu_cores=cpu_cores, memory_gb=memory_gb, gpu_count=gpu_count)
        self._repository.set_compute_allocation(alloc)
        return alloc

    def get_compute_allocation(self, workspace_id: UUID) -> ComputeAllocation | None:
        return self._repository.get_compute_allocation(workspace_id)

    def set_storage_allocation(self, workspace_id: UUID, storage_gb: int) -> StorageAllocation:
        alloc = StorageAllocation(workspace_id=workspace_id, storage_gb=storage_gb)
        self._repository.set_storage_allocation(alloc)
        return alloc

    def get_storage_allocation(self, workspace_id: UUID) -> StorageAllocation | None:
        return self._repository.get_storage_allocation(workspace_id)
