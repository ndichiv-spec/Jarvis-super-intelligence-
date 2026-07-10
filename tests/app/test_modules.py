"""Tests for banner, log, bootstrap modules."""

from __future__ import annotations

import pytest

from app.banner import print_banner
from app.bootstrap import bootstrap
from app.configuration import AppConfig
from app.kernel import AppKernel
from app.log import configure_logging, get_logger


class TestBanner:
    def test_print_banner_ready(self, capsys: pytest.CaptureFixture[str]) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_ready()
        print_banner(kernel, elapsed=1.23)
        captured = capsys.readouterr()
        assert "JARVIS" in captured.out
        assert "READY" in captured.out

    def test_print_banner_degraded(self, capsys: pytest.CaptureFixture[str]) -> None:
        kernel = AppKernel()
        kernel.initialize()
        kernel.mark_degraded("test")
        print_banner(kernel)
        captured = capsys.readouterr()
        assert "DEGRADED" in captured.out

    def test_print_banner_failed(self, capsys: pytest.CaptureFixture[str]) -> None:
        kernel = AppKernel()
        kernel.fail()
        print_banner(kernel)
        captured = capsys.readouterr()
        assert "FAILED" in captured.out


class TestLog:
    def test_configure_logging(self) -> None:
        configure_logging(level="INFO")

    def test_get_logger(self) -> None:
        logger = get_logger("test")
        assert logger.name == "test"

    def test_logger_writes(self, capsys: pytest.CaptureFixture[str]) -> None:
        configure_logging(level="DEBUG")
        logger = get_logger("test-log")
        logger.info("hello from test")
        captured = capsys.readouterr()
        assert "hello from test" in captured.out


class TestBootstrap:
    def test_bootstrap_returns_context(self) -> None:
        configure_logging(level="CRITICAL")
        ctx = bootstrap()
        assert ctx.kernel is not None
        assert ctx.kernel.registry.count() == 12

    def test_bootstrap_context_shutdown(self) -> None:
        configure_logging(level="CRITICAL")
        ctx = bootstrap()
        ctx.shutdown()
        assert ctx.kernel.lifecycle.state.value == "stopped"
