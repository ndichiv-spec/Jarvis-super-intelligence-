"""Governance domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class PolicyScope(StrEnum):
    global_ = "global"
    organization = "organization"
    workspace = "workspace"


class PolicyType(StrEnum):
    data_governance = "data_governance"
    retention = "retention"
    compliance = "compliance"
    security = "security"
    operational = "operational"


class PolicyEffect(StrEnum):
    allow = "allow"
    deny = "deny"
    audit = "audit"
    require = "require"


@dataclass(frozen=True, slots=True)
class PolicyRule:
    resource_pattern: str = "*"
    action_pattern: str = "*"
    effect: PolicyEffect = PolicyEffect.deny
    conditions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GovernancePolicy:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    scope: PolicyScope = PolicyScope.global_
    policy_type: PolicyType = PolicyType.operational
    enabled: bool = True
    rules: tuple[PolicyRule, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class DataGovernanceRule:
    id: UUID = field(default_factory=uuid4)
    data_type: str = ""
    classification: str = "internal"
    retention_days: int = 90
    requires_encryption: bool = True
    allowed_regions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    data_category: str = ""
    retention_days: int = 90
    archival_days: int = 365
    deletion_after_days: int = 730
    legal_hold: bool = False


@dataclass(frozen=True, slots=True)
class ComplianceControl:
    id: UUID = field(default_factory=uuid4)
    framework: str = ""
    control_id: str = ""
    description: str = ""
    implemented: bool = False
    evidence: str = ""
