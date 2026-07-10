"""Billing and licensing domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class SubscriptionTier(StrEnum):
    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"


class SubscriptionStatus(StrEnum):
    active = "active"
    trialing = "trialing"
    past_due = "past_due"
    canceled = "canceled"
    expired = "expired"


class LicenseType(StrEnum):
    per_user = "per_user"
    per_org = "per_org"
    usage_based = "usage_based"
    site = "site"


@dataclass(frozen=True, slots=True)
class SubscriptionPlan:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    tier: SubscriptionTier = SubscriptionTier.free
    max_users: int = 5
    max_workspaces: int = 1
    max_storage_gb: int = 10
    features: tuple[str, ...] = ()
    price_monthly: float = 0.0


@dataclass(frozen=True, slots=True)
class Subscription:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    plan_id: UUID = field(default_factory=uuid4)
    status: SubscriptionStatus = SubscriptionStatus.active
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime | None = None


@dataclass(frozen=True, slots=True)
class License:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    license_type: LicenseType = LicenseType.per_user
    max_seats: int = 0
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UsageRecord:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    metric: str = ""
    amount: float = 0.0
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class CostReport:
    org_id: UUID = field(default_factory=uuid4)
    period: str = ""
    total_cost: float = 0.0
    by_category: dict[str, float] = field(default_factory=dict)
