"""Tests for Resource Management."""

from uuid import uuid4

from jarvis_enterprise.resource_management.models import (
    ComputeAllocation,
    Quota,
    QuotaPeriod,
    ResourceType,
    StorageAllocation,
    UsagePolicy,
)
from jarvis_enterprise.resource_management.repository import ResourceRepository
from jarvis_enterprise.resource_management.service import ResourceManagementService


class InMemoryResourceRepo:
    def __init__(self):
        self._quotas: dict = {}
        self._usage: list = []
        self._policies: dict = {}
        self._compute: dict = {}
        self._storage: dict = {}

    def save_quota(self, quota) -> None:
        key = (quota.org_id, quota.resource_type.value, quota.resource_name)
        self._quotas[key] = quota

    def get_quota(self, org_id, resource_type, resource_name) -> Quota | None:
        return self._quotas.get((org_id, resource_type, resource_name))

    def list_quotas(self, org_id) -> list[Quota]:
        return [q for q in self._quotas.values() if q.org_id == org_id]

    def record_usage(self, usage) -> None:
        self._usage.append(usage)

    def get_usage(self, org_id, resource_type) -> list:
        return [u for u in self._usage if u.org_id == org_id]

    def save_usage_policy(self, policy) -> None:
        self._policies[policy.id] = policy

    def list_usage_policies(self) -> list[UsagePolicy]:
        return list(self._policies.values())

    def set_compute_allocation(self, alloc) -> None:
        self._compute[alloc.workspace_id] = alloc

    def get_compute_allocation(self, ws_id) -> ComputeAllocation | None:
        return self._compute.get(ws_id)

    def set_storage_allocation(self, alloc) -> None:
        self._storage[alloc.workspace_id] = alloc

    def get_storage_allocation(self, ws_id) -> StorageAllocation | None:
        return self._storage.get(ws_id)


class TestResourceService:
    def setup_method(self):
        self.repo = ResourceManagementService(InMemoryResourceRepo())

    def test_set_quota(self):
        quota = self.repo.set_quota(uuid4(), ResourceType.compute, "cpu", 100)
        assert quota.limit == 100

    def test_get_quota(self):
        org_id = uuid4()
        self.repo.set_quota(org_id, ResourceType.compute, "cpu", 100)
        quota = self.repo.get_quota(org_id, "compute", "cpu")
        assert quota is not None
        assert quota.limit == 100

    def test_check_quota_within(self):
        org_id = uuid4()
        self.repo.set_quota(org_id, ResourceType.compute, "cpu", 100)
        ok, remaining = self.repo.check_quota(org_id, "compute", "cpu")
        assert ok is True
        assert remaining == 100

    def test_check_quota_no_quota(self):
        ok, _ = self.repo.check_quota(uuid4(), "compute", "gpu")
        assert ok is True

    def test_record_usage(self):
        usage = self.repo.record_usage(uuid4(), uuid4(), ResourceType.ai_provider, "openai", 50)
        assert usage.amount == 50

    def test_create_usage_policy(self):
        policy = self.repo.create_usage_policy("AI Limits", ResourceType.ai_provider, 1000, 100)
        assert policy.max_per_org == 1000

    def test_compute_allocation(self):
        ws_id = uuid4()
        alloc = self.repo.set_compute_allocation(ws_id, 4, 16, 1)
        assert alloc.cpu_cores == 4
        assert alloc.gpu_count == 1

    def test_storage_allocation(self):
        ws_id = uuid4()
        alloc = self.repo.set_storage_allocation(ws_id, 500)
        assert alloc.storage_gb == 500
