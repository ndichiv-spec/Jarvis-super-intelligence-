"""Tests for kernel."""

from __future__ import annotations

import pytest

from app.configuration import AppConfig
from app.health import HealthStatus
from app.kernel import AppKernel
from app.lifecycle import LifecycleState
from app.registry import ServiceStatus


class TestAppKernel:
    def test_create_default_config(self) -> None:
        kernel = AppKernel()
        assert isinstance(kernel.config, AppConfig)
        assert kernel.state.version == "2.0.0"

    def test_create_with_config(self) -> None:
        config = AppConfig(profile="test", debug=False)
        kernel = AppKernel(config)
        assert kernel.config.profile == "test"
        assert kernel.config.debug is False

    def test_initial_lifecycle_state(self) -> None:
        kernel = AppKernel()
        assert kernel.lifecycle.state == LifecycleState.created

    def test_initial_registry_empty(self) -> None:
        kernel = AppKernel()
        assert kernel.registry.count() == 0

    def test_initial_health_unknown(self) -> None:
        kernel = AppKernel()
        report = kernel.health.get_report()
        assert report.platform == HealthStatus.unknown

    def test_initialize_transitions_to_starting(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        assert kernel.lifecycle.state == LifecycleState.starting
        assert kernel.registry.count() == 12

    def test_initialize_registers_platform_services(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        for svc_id in ("security", "memory", "knowledge", "ai", "communication", "automation", "extensions", "infrastructure", "gateway", "orchestration", "agents", "enterprise"):
            svc = kernel.registry.get(svc_id)
            assert svc is not None, f"Service {svc_id} not registered"
            assert svc.status == ServiceStatus.registered

    def test_initialize_reports_health_for_each(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = kernel.health.get_report()
        assert len(report.checks) == 12

    def test_mark_ready(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_ready()
        assert kernel.lifecycle.state == LifecycleState.ready
        assert kernel.state.initialized is True
        assert kernel.state.started_at is not None

    def test_mark_degraded(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_degraded("test")
        assert kernel.lifecycle.state == LifecycleState.degraded

    def test_shutdown(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_ready()
        kernel.shutdown()
        assert kernel.lifecycle.state == LifecycleState.stopped

    def test_fail(self) -> None:
        kernel = AppKernel()
        kernel.fail()
        assert kernel.lifecycle.state == LifecycleState.failed

    def test_fail_with_reason(self) -> None:
        kernel = AppKernel()
        kernel.fail("something broke")
        assert kernel.lifecycle.state == LifecycleState.failed

    def test_get_health_report(self) -> None:
        kernel = AppKernel()
        report = kernel.get_health_report()
        assert report.platform == HealthStatus.unknown

    def test_initialize_then_get_health_report(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = kernel.get_health_report()
        assert len(report.checks) == 12

    def test_kernel_state_service_count(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_ready()
        assert kernel.state.services_count == 12

    def test_properties(self) -> None:
        kernel = AppKernel()
        assert kernel.config is not None
        assert kernel.lifecycle is not None
        assert kernel.registry is not None
        assert kernel.health is not None
        assert kernel.state is not None

    def test_health_after_initialize_has_all_unknown(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        report = kernel.health.get_report()
        for c in report.checks:
            assert c.status == HealthStatus.unknown

    def test_platform_services_have_capabilities(self) -> None:
        kernel = AppKernel()
        kernel.initialize()
        svc = kernel.registry.get("security")
        assert svc is not None
        assert "authn" in svc.capabilities
