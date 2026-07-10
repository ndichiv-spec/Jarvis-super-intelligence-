"""Disaster Recovery plan - RPO/RTO, failover strategy, data restoration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DrTier(StrEnum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"


class FailoverMode(StrEnum):
    manual = "manual"
    semi_automated = "semi_automated"
    fully_automated = "fully_automated"


@dataclass(frozen=True)
class RecoveryObjective:
    rpo_minutes: int
    rto_minutes: int


@dataclass(frozen=True)
class DrPlan:
    tier: DrTier
    objectives: RecoveryObjective
    failover_mode: FailoverMode
    backup_regions: list[str] = field(default_factory=list)
    documentation_refs: list[str] = field(default_factory=list)
    runbooks: list[str] = field(default_factory=list)


DR_PLANS: dict[DrTier, DrPlan] = {
    DrTier.bronze: DrPlan(
        tier=DrTier.bronze,
        objectives=RecoveryObjective(rpo_minutes=1440, rto_minutes=480),
        failover_mode=FailoverMode.manual,
    ),
    DrTier.silver: DrPlan(
        tier=DrTier.silver,
        objectives=RecoveryObjective(rpo_minutes=240, rto_minutes=120),
        failover_mode=FailoverMode.semi_automated,
    ),
    DrTier.gold: DrPlan(
        tier=DrTier.gold,
        objectives=RecoveryObjective(rpo_minutes=60, rto_minutes=30),
        failover_mode=FailoverMode.semi_automated,
        backup_regions=["us-west-2", "eu-west-1"],
    ),
    DrTier.platinum: DrPlan(
        tier=DrTier.platinum,
        objectives=RecoveryObjective(rpo_minutes=5, rto_minutes=5),
        failover_mode=FailoverMode.fully_automated,
        backup_regions=["us-west-2", "eu-west-1", "ap-southeast-1"],
    ),
}


class DisasterRecovery:
    def __init__(self, tier: DrTier = DrTier.gold) -> None:
        self._plan = DR_PLANS[tier]

    @property
    def plan(self) -> DrPlan:
        return self._plan

    def get_runbooks(self) -> list[str]:
        return [
            "dr-runbook-failover.md",
            "dr-runbook-data-restore.md",
            "dr-runbook-service-restore.md",
            "dr-runbook-verification.md",
        ]

    def get_recovery_steps(self, scenario: str) -> list[str]:
        steps: dict[str, list[str]] = {
            "region_failure": [
                "1. Verify region outage via health monitoring",
                "2. Activate failover to secondary region",
                "3. Promote replica database to primary",
                "4. Update DNS records to secondary region",
                "5. Verify service health in secondary region",
                "6. Scale services to match primary capacity",
                "7. Verify data consistency",
                "8. Notify stakeholders",
            ],
            "data_corruption": [
                "1. Isolate affected services",
                "2. Identify last valid backup",
                "3. Restore database from backup",
                "4. Verify data integrity",
                "5. Re-apply any lost transactions from WAL",
                "6. Re-enable services",
                "7. Verify application health",
            ],
            "service_failure": [
                "1. Identify failed services via health checks",
                "2. Check pod logs for root cause",
                "3. Scale affected pods if resource issue",
                "4. Rollback to last known good release if code issue",
                "5. Verify dependent services",
                "6. Verify end-to-end health",
            ],
        }
        return steps.get(scenario, ["No predefined steps for this scenario"])

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self._plan.objectives.rpo_minutes <= 0:
            issues.append("RPO must be > 0")
        if self._plan.objectives.rto_minutes <= 0:
            issues.append("RTO must be > 0")
        if self._plan.tier in (DrTier.gold, DrTier.platinum) and not self._plan.backup_regions:
            issues.append(f"Tier {self._plan.tier.value} requires backup regions")
        return issues
