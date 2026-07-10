"""Tests for runtime facade."""

from __future__ import annotations

import pytest

from app.runtime import Runtime


class TestRuntime:
    def test_initial_state_not_running(self) -> None:
        rt = Runtime()
        assert rt.kernel is None
        assert rt.config is None
        assert rt.registry is None
        assert rt.state is None

    def test_initial_health(self) -> None:
        rt = Runtime()
        assert rt.health() == {"platform": "not_running", "summary": "", "checks": [], "processes": {}, "process_checks": []}

    def test_initial_status(self) -> None:
        rt = Runtime()
        assert rt.status() == {"status": "not_running"}

    def test_start_returns_kernel(self) -> None:
        rt = Runtime()
        kernel = rt.start(start_apps=False)
        assert kernel is not None
        assert rt.kernel is kernel

    def test_start_makes_kernel_available(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        assert rt.kernel is not None
        assert rt.config is not None
        assert rt.registry is not None
        assert rt.state is not None

    def test_start_with_config_path(self) -> None:
        rt = Runtime()
        kernel = rt.start("", start_apps=False)
        assert kernel is not None

    def test_stop(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        rt.stop()
        assert rt.kernel is None

    def test_stop_when_not_running(self) -> None:
        rt = Runtime()
        rt.stop()

    def test_restart(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        kernel = rt.restart()
        assert kernel is not None
        assert rt.kernel is not None

    def test_restart_when_not_running(self) -> None:
        rt = Runtime()
        kernel = rt.restart()
        assert kernel is not None

    def test_health_after_start(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        health = rt.health()
        assert "platform" in health
        assert "summary" in health
        assert "checks" in health

    def test_status_after_start(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        status = rt.status()
        assert "status" in status
        assert "services" in status
        assert "version" in status
        assert status["services"] == 12

    def test_diagnostics_after_start(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        diag = rt.diagnostics()
        assert diag.services
        assert diag.platform_info

    def test_diagnostics_raises_when_not_running(self) -> None:
        rt = Runtime()
        with pytest.raises(RuntimeError, match="not running"):
            rt.diagnostics()

    def test_lifecycle_after_start(self) -> None:
        rt = Runtime()
        rt.start(start_apps=False)
        assert rt.kernel.lifecycle.state.value == "starting"
