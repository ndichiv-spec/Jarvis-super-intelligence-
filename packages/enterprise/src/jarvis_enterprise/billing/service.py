"""Billing preparation service — subscription, license, usage architecture."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from jarvis_enterprise.billing.models import (
    CostReport,
    License,
    LicenseType,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    SubscriptionTier,
    UsageRecord,
)
from jarvis_enterprise.billing.repository import BillingRepository


class BillingPreparationService:
    def __init__(self, repository: BillingRepository) -> None:
        self._repository = repository

    def create_plan(
        self, name: str, tier: SubscriptionTier, max_users: int,
        max_workspaces: int, max_storage_gb: int, price_monthly: float = 0.0,
    ) -> SubscriptionPlan:
        plan = SubscriptionPlan(
            name=name, tier=tier, max_users=max_users,
            max_workspaces=max_workspaces, max_storage_gb=max_storage_gb,
            price_monthly=price_monthly,
        )
        self._repository.save_plan(plan)
        return plan

    def list_plans(self) -> list[SubscriptionPlan]:
        return self._repository.list_plans()

    def create_subscription(self, org_id: UUID, plan_id: UUID) -> Subscription:
        sub = Subscription(org_id=org_id, plan_id=plan_id)
        self._repository.save_subscription(sub)
        return sub

    def get_subscription(self, org_id: UUID) -> Subscription | None:
        return self._repository.get_subscription(org_id)

    def cancel_subscription(self, org_id: UUID) -> Subscription | None:
        sub = self._repository.get_subscription(org_id)
        if sub is None:
            return None
        updated = Subscription(
            id=sub.id, org_id=sub.org_id, plan_id=sub.plan_id,
            status=SubscriptionStatus.canceled,
            start_date=sub.start_date, end_date=datetime.now(timezone.utc),
        )
        self._repository.save_subscription(updated)
        return updated

    def issue_license(self, org_id: UUID, license_type: LicenseType, max_seats: int) -> License:
        lic = License(org_id=org_id, license_type=license_type, max_seats=max_seats)
        self._repository.save_license(lic)
        return lic

    def get_license(self, org_id: UUID) -> License | None:
        return self._repository.get_license(org_id)

    def record_usage(self, org_id: UUID, metric: str, amount: float) -> UsageRecord:
        record = UsageRecord(org_id=org_id, metric=metric, amount=amount)
        self._repository.record_usage(record)
        return record

    def generate_cost_report(self, org_id: UUID, period: str) -> CostReport:
        usage = self._repository.get_usage(org_id, period)
        by_category: dict[str, float] = {}
        total = 0.0
        for record in usage:
            by_category[record.metric] = by_category.get(record.metric, 0.0) + record.amount
            total += record.amount
        report = CostReport(org_id=org_id, period=period, total_cost=total, by_category=by_category)
        self._repository.save_cost_report(report)
        return report
