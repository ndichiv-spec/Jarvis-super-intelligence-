"""High Availability Design - redundant services, health monitoring, failover."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FailoverStrategy(StrEnum):
    active_passive = "active_passive"
    active_active = "active_active"
    hot_standby = "hot_standby"


class UpdateStrategy(StrEnum):
    rolling = "rolling"
    blue_green = "blue_green"
    canary = "canary"


@dataclass(frozen=True)
class HealthCheckConfig:
    path: str = "/health"
    interval_seconds: int = 15
    timeout_seconds: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3


@dataclass(frozen=True)
class RedundancyConfig:
    replicas_per_az: int = 1
    availability_zones: int = 3
    failover_strategy: FailoverStrategy = FailoverStrategy.active_active
    health_check: HealthCheckConfig = field(default_factory=HealthCheckConfig)


@dataclass(frozen=True)
class RollingUpdateConfig:
    max_surge: str = "25%"
    max_unavailable: str = "25%"
    min_ready_seconds: int = 30
    progress_deadline_seconds: int = 600


@dataclass(frozen=True)
class BlueGreenDeploymentConfig:
    auto_promote_seconds: int = 300
    analysis_duration: int = 120
    verify_replicas: int = 1


@dataclass(frozen=True)
class HighAvailabilityDesign:
    redundancy: RedundancyConfig = field(default_factory=RedundancyConfig)
    update_strategy: UpdateStrategy = UpdateStrategy.rolling
    rolling_update: RollingUpdateConfig = field(default_factory=RollingUpdateConfig)
    blue_green: BlueGreenDeploymentConfig | None = None
    pod_disruption_budget_min_available: int | str = 1
    anti_affinity: bool = True
    topology_spread: bool = True


DEFAULT_HA = HighAvailabilityDesign()

PRODUCTION_HA = HighAvailabilityDesign(
    redundancy=RedundancyConfig(replicas_per_az=2, availability_zones=3),
    update_strategy=UpdateStrategy.blue_green,
    rolling_update=RollingUpdateConfig(),
    blue_green=BlueGreenDeploymentConfig(auto_promote_seconds=300),
    pod_disruption_budget_min_available="50%",
    anti_affinity=True,
    topology_spread=True,
)
