"""Scaling Policies - horizontal, vertical, queue-based, and scheduled scaling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ScalingMetric(StrEnum):
    cpu = "cpu"
    memory = "memory"
    requests_per_second = "requests_per_second"
    queue_depth = "queue_depth"
    concurrent_sessions = "concurrent_sessions"


class ScalingStrategy(StrEnum):
    horizontal = "horizontal"
    vertical = "vertical"
    queue_based = "queue_based"
    scheduled = "scheduled"


@dataclass(frozen=True)
class ScalingRule:
    metric: ScalingMetric
    threshold: float
    operator: str = "gt"
    cooldown_seconds: int = 300
    scale_up_by: int = 1
    scale_down_by: int = 1


@dataclass(frozen=True)
class HorizontalScalingPolicy:
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    rules: list[ScalingRule] = field(default_factory=list)


@dataclass(frozen=True)
class VerticalScalingPolicy:
    min_cpu: str = "250m"
    max_cpu: str = "4"
    min_memory: str = "256Mi"
    max_memory: str = "8Gi"
    resize_interval: int = 600


@dataclass(frozen=True)
class QueueBasedScalingPolicy:
    queue_name: str
    target_queue_length: int = 100
    max_workers: int = 20
    scale_up_threshold: int = 50
    scale_down_threshold: int = 10


@dataclass(frozen=True)
class ScheduledScalingRule:
    schedule: str
    replicas: int
    timezone: str = "UTC"
    description: str = ""


@dataclass(frozen=True)
class ScalingPolicySet:
    service: str
    horizontal: HorizontalScalingPolicy = field(default_factory=HorizontalScalingPolicy)
    vertical: VerticalScalingPolicy | None = None
    queue_based: QueueBasedScalingPolicy | None = None
    scheduled_rules: list[ScheduledScalingRule] = field(default_factory=list)


DEFAULT_POLICIES: dict[str, ScalingPolicySet] = {
    "api": ScalingPolicySet(
        service="api",
        horizontal=HorizontalScalingPolicy(min_replicas=2, max_replicas=10),
    ),
    "brain": ScalingPolicySet(
        service="brain",
        horizontal=HorizontalScalingPolicy(min_replicas=2, max_replicas=8),
    ),
    "ai": ScalingPolicySet(
        service="ai",
        horizontal=HorizontalScalingPolicy(min_replicas=2, max_replicas=15),
    ),
    "automation": ScalingPolicySet(
        service="automation",
        horizontal=HorizontalScalingPolicy(min_replicas=1, max_replicas=5),
    ),
}


class ScalingPolicyEngine:
    def __init__(self) -> None:
        self._policies: dict[str, ScalingPolicySet] = dict(DEFAULT_POLICIES)

    def get_policy(self, service: str) -> ScalingPolicySet | None:
        return self._policies.get(service)

    def list_policies(self) -> dict[str, ScalingPolicySet]:
        return dict(self._policies)

    def set_policy(self, service: str, policy: ScalingPolicySet) -> None:
        self._policies[service] = policy

    def validate(self) -> list[str]:
        issues: list[str] = []
        for service, policy in self._policies.items():
            if policy.horizontal.min_replicas > policy.horizontal.max_replicas:
                issues.append(f"Service '{service}': min_replicas > max_replicas")
            if policy.horizontal.min_replicas < 1:
                issues.append(f"Service '{service}': min_replicas must be >= 1")
            if policy.queue_based:
                q = policy.queue_based
                if q.scale_up_threshold >= q.target_queue_length:
                    issues.append(f"Service '{service}': scale_up_threshold should be < target_queue_length")
        return issues
