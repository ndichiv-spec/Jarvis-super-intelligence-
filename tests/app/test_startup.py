"""Tests for startup and shutdown."""

from __future__ import annotations

import pytest

from app.log import configure_logging
from app.startup import run_startup


class TestStartup:
    def test_run_startup_returns_kernel(self) -> None:
        configure_logging(level="CRITICAL")
        kernel = run_startup()
        assert kernel is not None

    def test_run_startup_has_services(self) -> None:
        configure_logging(level="CRITICAL")
        kernel = run_startup()
        assert kernel.registry.count() == 12

    def test_run_startup_starting_state(self) -> None:
        configure_logging(level="CRITICAL")
        kernel = run_startup()
        assert kernel.lifecycle.state.value == "starting"

    def test_run_startup_services_running(self) -> None:
        configure_logging(level="CRITICAL")
        kernel = run_startup()
        for svc in kernel.registry.list():
            assert svc.status.value == "running", f"{svc.id} not running"

    def test_run_startup_with_config_path(self) -> None:
        configure_logging(level="CRITICAL")
        kernel = run_startup(config_path="")
        assert kernel is not None
