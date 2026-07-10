"""Tests for diagnostics."""

from __future__ import annotations

import pytest

from app.diagnostics import DiagnosticReport, generate_report, print_report
from app.health import HealthStatus
from app.kernel import AppKernel
from app.lifecycle import LifecycleState


class TestDiagnostics:
    def test_generate_report_has_all_fields(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_ready()
        report = generate_report(kernel)
        assert report.timestamp is not None
        assert report.platform_info
        assert report.python_info
        assert report.config_summary
        assert report.services
        assert report.lifecycle
        assert report.health
        assert report.dependency_graph

    def test_report_has_platform_info(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert "system" in report.platform_info
        assert "machine" in report.platform_info

    def test_report_has_python_info(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert "version" in report.python_info
        assert "executable" in report.python_info

    def test_report_has_config_summary(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert report.config_summary.get("profile") == "development"
        assert report.config_summary.get("debug") is False

    def test_report_has_services(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = generate_report(kernel)
        assert len(report.services) == 12

    def test_report_has_lifecycle(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert "state" in report.lifecycle
        assert "history" in report.lifecycle

    def test_report_has_health(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert "platform" in report.health
        assert "checks" in report.health

    def test_report_has_dependency_graph(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = generate_report(kernel)
        assert len(report.dependency_graph) > 0

    def test_report_warns_default_secret(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert any("secret" in w.lower() for w in report.warnings)

    def test_print_report_does_not_raise(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        print_report(report)

    def test_print_report_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        print_report(report)
        captured = capsys.readouterr()
        assert "timestamp" in captured.out

    def test_health_in_report(self) -> None:
        kernel = AppKernel()
        report = generate_report(kernel)
        assert report.health["platform"] == "unknown"

    def test_services_list_after_initialize(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = generate_report(kernel)
        ids = [s["id"] for s in report.services]
        assert "security" in ids
        assert "memory" in ids
        assert "enterprise" in ids

    def test_priority_error_in_health(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.health.report("test", HealthStatus.error, "fail")  # type: ignore[name-defined]
        report = generate_report(kernel)
        assert report.health["platform"] == "error"

    def test_dependency_graph_structure(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = generate_report(kernel)
        assert isinstance(report.dependency_graph, dict)
        assert "security" in report.dependency_graph
