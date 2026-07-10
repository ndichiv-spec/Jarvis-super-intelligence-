"""Tests for health monitor."""

from __future__ import annotations

from app.health import HealthCheck, HealthMonitor, HealthReport, HealthStatus


class TestHealthCheck:
    def test_create(self) -> None:
        c = HealthCheck(subsystem="test", status=HealthStatus.ready, message="ok")
        assert c.subsystem == "test"
        assert c.status == HealthStatus.ready
        assert c.message == "ok"


class TestHealthMonitor:
    def test_initial_report_empty(self) -> None:
        m = HealthMonitor()
        report = m.get_report()
        assert report.platform == HealthStatus.unknown
        assert report.checks == ()

    def test_report_single_ready(self) -> None:
        m = HealthMonitor()
        m.report("svc1", HealthStatus.ready, "ok")
        report = m.get_report()
        assert report.platform == HealthStatus.ready
        assert len(report.checks) == 1

    def test_report_error_overrides(self) -> None:
        m = HealthMonitor()
        m.report("svc1", HealthStatus.ready, "ok")
        m.report("svc2", HealthStatus.error, "fail")
        report = m.get_report()
        assert report.platform == HealthStatus.error

    def test_report_warning(self) -> None:
        m = HealthMonitor()
        m.report("svc1", HealthStatus.ready, "ok")
        m.report("svc2", HealthStatus.warning, "warn")
        report = m.get_report()
        assert report.platform == HealthStatus.warning

    def test_report_unknown(self) -> None:
        m = HealthMonitor()
        m.report("svc1", HealthStatus.unknown, "?")
        report = m.get_report()
        assert report.platform == HealthStatus.unknown

    def test_priority_error_over_warning(self) -> None:
        m = HealthMonitor()
        m.report("s1", HealthStatus.warning, "warn")
        m.report("s2", HealthStatus.error, "err")
        assert m.get_report().platform == HealthStatus.error

    def test_priority_warning_over_ready(self) -> None:
        m = HealthMonitor()
        m.report("s1", HealthStatus.ready, "ok")
        m.report("s2", HealthStatus.warning, "warn")
        assert m.get_report().platform == HealthStatus.warning

    def test_priority_ready_over_unknown(self) -> None:
        m = HealthMonitor()
        m.report("s1", HealthStatus.unknown, "?")
        m.report("s2", HealthStatus.ready, "ok")
        assert m.get_report().platform == HealthStatus.ready

    def test_multiple_checks(self) -> None:
        m = HealthMonitor()
        m.report("a", HealthStatus.ready, "ok")
        m.report("b", HealthStatus.warning, "warn")
        m.report("c", HealthStatus.error, "err")
        report = m.get_report()
        assert len(report.checks) == 3

    def test_summary_empty(self) -> None:
        m = HealthMonitor()
        assert m.get_report().summary == "No health checks reported"

    def test_summary_with_checks(self) -> None:
        m = HealthMonitor()
        m.report("a", HealthStatus.ready, "ok")
        report = m.get_report()
        assert "ready" in report.summary


class TestHealthReport:
    def test_frozen(self) -> None:
        r = HealthReport(platform=HealthStatus.ready, checks=(), summary="ok")
        assert r.platform == HealthStatus.ready
