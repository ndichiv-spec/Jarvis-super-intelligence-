"""Tests for Enterprise Observability."""

from uuid import uuid4

from jarvis_enterprise.observability.models import (
    PerformanceTrend,
    PlatformHealth,
    ServiceAvailability,
    ServiceHealth,
    ServiceStatus,
    UsageMetric,
)
from jarvis_enterprise.observability.service import EnterpriseObservabilityService


class TestObservabilityService:
    def setup_method(self):
        self.repo = EnterpriseObservabilityService()

    def test_report_service_health(self):
        health = self.repo.report_service_health("api", ServiceStatus.healthy, 12.5)
        assert health.service_name == "api"
        assert health.latency_ms == 12.5

    def test_platform_health(self):
        self.repo.report_service_health("api", ServiceStatus.healthy)
        self.repo.report_service_health("brain", ServiceStatus.healthy)
        platform = self.repo.get_platform_health(uuid4())
        assert platform.total_services == 2
        assert platform.healthy_services == 2

    def test_degraded_platform(self):
        self.repo.report_service_health("api", ServiceStatus.healthy)
        self.repo.report_service_health("brain", ServiceStatus.degraded)
        platform = self.repo.get_platform_health(uuid4())
        assert platform.overall_status == ServiceStatus.degraded

    def test_unhealthy_platform(self):
        self.repo.report_service_health("api", ServiceStatus.unhealthy)
        platform = self.repo.get_platform_health(uuid4())
        assert platform.overall_status == ServiceStatus.unhealthy

    def test_record_usage(self):
        metric = self.repo.record_usage("api_requests", uuid4(), 1000, {"api": 800, "brain": 200})
        assert metric.total == 1000

    def test_record_availability(self):
        av = self.repo.record_availability("api", 99.95, 10)
        assert av.availability_pct == 99.95
        assert av.downtime_minutes == 10

    def test_performance_trend(self):
        org_id = uuid4()
        self.repo.record_usage("api_requests", org_id, 100)
        self.repo.record_usage("api_requests", org_id, 150)
        trend = self.repo.get_performance_trend("api_requests")
        assert trend is not None
        assert trend.trend == "increasing"

    def test_performance_trend_insufficient_data(self):
        trend = self.repo.get_performance_trend("unknown")
        assert trend is None
