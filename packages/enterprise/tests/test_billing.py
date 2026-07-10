"""Tests for Billing & Licensing Preparation."""

from uuid import uuid4

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
from jarvis_enterprise.billing.service import BillingPreparationService


class InMemoryBillingRepo:
    def __init__(self):
        self._plans: dict = {}
        self._subscriptions: dict = {}
        self._licenses: dict = {}
        self._usage: list = []
        self._reports: dict = {}

    def save_plan(self, plan) -> None:
        self._plans[plan.id] = plan

    def get_plan(self, plan_id) -> SubscriptionPlan | None:
        return self._plans.get(plan_id)

    def list_plans(self) -> list[SubscriptionPlan]:
        return list(self._plans.values())

    def save_subscription(self, sub) -> None:
        self._subscriptions[sub.org_id] = sub

    def get_subscription(self, org_id) -> Subscription | None:
        return self._subscriptions.get(org_id)

    def save_license(self, lic) -> None:
        self._licenses[lic.org_id] = lic

    def get_license(self, org_id) -> License | None:
        return self._licenses.get(org_id)

    def record_usage(self, record) -> None:
        self._usage.append(record)

    def get_usage(self, org_id, period) -> list[UsageRecord]:
        return [u for u in self._usage if u.org_id == org_id]

    def save_cost_report(self, report) -> None:
        key = (report.org_id, report.period)
        self._reports[key] = report

    def get_cost_report(self, org_id, period) -> CostReport | None:
        return self._reports.get((org_id, period))


class TestBillingService:
    def setup_method(self):
        self.repo = BillingPreparationService(InMemoryBillingRepo())

    def test_create_plan(self):
        plan = self.repo.create_plan("Enterprise", SubscriptionTier.enterprise, 100, 50, 1000, 999.0)
        assert plan.tier == SubscriptionTier.enterprise
        assert plan.price_monthly == 999.0

    def test_list_plans(self):
        self.repo.create_plan("Free", SubscriptionTier.free, 5, 1, 10)
        self.repo.create_plan("Pro", SubscriptionTier.professional, 50, 10, 100)
        assert len(self.repo.list_plans()) == 2

    def test_create_subscription(self):
        plan = self.repo.create_plan("Test", SubscriptionTier.starter, 10, 5, 50)
        sub = self.repo.create_subscription(uuid4(), plan.id)
        assert sub.status == SubscriptionStatus.active

    def test_cancel_subscription(self):
        plan = self.repo.create_plan("Test", SubscriptionTier.starter, 10, 5, 50)
        org_id = uuid4()
        self.repo.create_subscription(org_id, plan.id)
        canceled = self.repo.cancel_subscription(org_id)
        assert canceled is not None
        assert canceled.status == SubscriptionStatus.canceled

    def test_issue_license(self):
        lic = self.repo.issue_license(uuid4(), LicenseType.per_user, 100)
        assert lic.max_seats == 100

    def test_record_usage(self):
        record = self.repo.record_usage(uuid4(), "api_calls", 1500.0)
        assert record.amount == 1500.0

    def test_generate_cost_report(self):
        org_id = uuid4()
        self.repo.record_usage(org_id, "api_calls", 100.0)
        self.repo.record_usage(org_id, "storage", 50.0)
        report = self.repo.generate_cost_report(org_id, "2026-06")
        assert report.total_cost == 150.0
        assert "api_calls" in report.by_category
