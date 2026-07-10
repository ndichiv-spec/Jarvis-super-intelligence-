"""Integration tests for INT-001: Process Manager, Gateway, Home, Browser."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

import pytest

from app.process_manager import ManagedProcess, ProcessManager
from app.browser import open_browser
from app.runtime import Runtime
from app.log import configure_logging


def test_managed_process_create() -> None:
    proc = ManagedProcess(id="test", name="Test", command=["python", "-c", "print('ok')"])
    assert proc.id == "test"
    assert proc.name == "Test"
    assert proc.process is None
    assert proc.started_at is None
    assert proc.restarts == 0
    assert proc.max_restarts == 3


def test_managed_process_defaults() -> None:
    proc = ManagedProcess(id="a", name="A", command=["echo"])
    assert proc.host == "127.0.0.1"
    assert proc.port == 0
    assert proc.health_path == "/"
    assert proc.cwd is None
    assert proc.env is None


class TestProcessManager:
    def test_start_stop_short_lived(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(id="test", name="Test", command=[sys.executable, "-c", "print('ok')"]))
        assert pm.start("test") is True
        time.sleep(0.3)
        assert pm.is_alive("test") is False
        pm.stop("test")

    def test_stop_nonexistent(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        assert pm.stop("nonexistent") is True

    def test_start_nonexistent(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        assert pm.start("nonexistent") is False

    def test_double_start(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(id="test", name="Test", command=[sys.executable, "-c", "print('ok')"]))
        assert pm.start("test") is True
        assert pm.start("test") is True
        pm.stop("test")

    def test_is_alive_nonexistent(self) -> None:
        pm = ProcessManager()
        assert pm.is_alive("nonexistent") is False

    def test_is_healthy_no_port(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(id="test", name="Test", command=[sys.executable, "-c", "import time; time.sleep(10)"]))
        pm.start("test")
        time.sleep(0.2)
        assert pm.is_healthy("test") is True
        pm.stop("test")

    def test_health_report_format(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        report = pm.health_report()
        assert isinstance(report, dict)
        pm.add(ManagedProcess(id="a", name="A", command=[sys.executable, "-c", "import time; time.sleep(10)"]))
        pm.start("a")
        time.sleep(0.2)
        report = pm.health_report()
        assert "a" in report
        info = report["a"]
        assert "pid" in info
        assert "port" in info
        assert "alive" in info
        assert "healthy" in info
        assert "restarts" in info
        assert "uptime" in info
        assert info["alive"] is True
        pm.stop("a")

    def test_stop_all(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(id="a", name="A", command=[sys.executable, "-c", "import time; time.sleep(10)"]))
        pm.add(ManagedProcess(id="b", name="B", command=[sys.executable, "-c", "import time; time.sleep(10)"]))
        pm.start("a")
        pm.start("b")
        time.sleep(0.2)
        pm.stop_all()
        assert pm.is_alive("a") is False
        assert pm.is_alive("b") is False

    def test_context_manager(self) -> None:
        configure_logging(level="CRITICAL")
        with ProcessManager() as pm:
            pm.add(ManagedProcess(id="a", name="A", command=[sys.executable, "-c", "import time; time.sleep(10)"]))
            pm.start("a")
            time.sleep(0.2)
            assert pm.is_alive("a") is True
        assert pm.is_alive("a") is False

    def test_wait_for_ready_timeout(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(id="test", name="Test", command=[sys.executable, "-c", "import time; time.sleep(10)"],
                              port=0))
        pm.start("test")
        ready = pm.wait_for_ready("test", timeout=1.0, interval=0.1)
        assert ready is True
        pm.stop("test")


class TestProcessManagerHTTP:
    """Test HTTP health checks using a temporary HTTP server."""

    @staticmethod
    def _serve_ok(server: HTTPServer) -> None:
        server.serve_forever(poll_interval=0.05)

    def test_http_health_check(self) -> None:
        configure_logging(level="CRITICAL")

        class OKHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
            def log_message(self, *args: object) -> None:
                pass

        server = HTTPServer(("127.0.0.1", 0), OKHandler)
        port = server.server_port
        thread = Thread(target=self._serve_ok, args=(server,), daemon=True)
        thread.start()
        time.sleep(0.2)

        pm = ProcessManager()
        pm.add(ManagedProcess(
            id="test_http", name="HTTP Test",
            command=[sys.executable, "-c", "import time; time.sleep(30)"],
            host="127.0.0.1", port=port, health_path="/",
        ))
        pm.start("test_http")
        time.sleep(0.2)
        assert pm.is_alive("test_http") is True
        assert pm.is_healthy("test_http", timeout=2.0) is True
        pm.stop("test_http")
        server.shutdown()

    def test_http_health_check_failure(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(
            id="bad_http", name="Bad HTTP",
            command=[sys.executable, "-c", "import time; time.sleep(30)"],
            host="127.0.0.1", port=19999, health_path="/",
        ))
        pm.start("bad_http")
        time.sleep(0.2)
        assert pm.is_healthy("bad_http", timeout=1.0) is False
        pm.stop("bad_http")

    def test_wait_for_ready_http(self) -> None:
        configure_logging(level="CRITICAL")

        class SlowOKHandler(BaseHTTPRequestHandler):
            started = False
            def do_GET(self) -> None:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
            def log_message(self, *args: object) -> None:
                pass

        server = HTTPServer(("127.0.0.1", 0), SlowOKHandler)
        port = server.server_port
        thread = Thread(target=self._serve_ok, args=(server,), daemon=True)
        thread.start()
        time.sleep(0.2)

        pm = ProcessManager()
        pm.add(ManagedProcess(
            id="slow", name="Slow",
            command=[sys.executable, "-c", "import time; time.sleep(30)"],
            host="127.0.0.1", port=port, health_path="/",
        ))
        pm.start("slow")
        ready = pm.wait_for_ready("slow", timeout=5.0, interval=0.1)
        assert ready is True
        pm.stop("slow")
        server.shutdown()

    def test_wait_for_ready_timeout_no_server(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(
            id="nowhere", name="Nowhere",
            command=[sys.executable, "-c", "import time; time.sleep(30)"],
            host="127.0.0.1", port=29888, health_path="/",
        ))
        pm.start("nowhere")
        ready = pm.wait_for_ready("nowhere", timeout=0.5, interval=0.1)
        assert ready is False
        pm.stop("nowhere")


class TestBrowser:
    def test_open_browser_disabled(self) -> None:
        configure_logging(level="CRITICAL")
        open_browser("http://localhost:0", enabled=False)

    def test_open_browser_enabled(self) -> None:
        configure_logging(level="CRITICAL")
        open_browser("http://localhost:0", enabled=True)


class TestRuntimeIntegration:
    def test_process_manager_property(self) -> None:
        rt = Runtime()
        assert rt.process_manager is not None
        assert rt.process_manager.health_report() == {}

    def test_health_structure(self) -> None:
        configure_logging(level="CRITICAL")
        rt = Runtime()
        rt.start(start_apps=False)
        report = rt.health()
        assert "processes" in report
        assert "process_checks" in report
        assert isinstance(report["processes"], dict)
        rt.stop()

    def test_status_structure(self) -> None:
        configure_logging(level="CRITICAL")
        rt = Runtime()
        rt.start(start_apps=False)
        status = rt.status()
        assert "processes" in status
        rt.stop()

    def test_restart_without_apps(self) -> None:
        configure_logging(level="CRITICAL")
        rt = Runtime()
        kernel = rt.restart(start_apps=False)
        assert kernel is not None
        assert kernel.lifecycle.state.value == "starting"
        rt.stop()

    def test_start_apps_and_stop(self) -> None:
        configure_logging(level="CRITICAL")
        rt = Runtime()
        kernel = rt.start(start_apps=True)
        assert kernel is not None
        rt.stop()
        assert rt.kernel is None

    def test_start_apps_health_report(self) -> None:
        configure_logging(level="CRITICAL")
        rt = Runtime()
        rt.start(start_apps=True)
        report = rt.health()
        assert "processes" in report
        assert "process_checks" in report
        gateway = report["processes"].get("gateway", {})
        assert "pid" in gateway
        rt.stop()


class TestGatewayEntry:
    def test_gateway_entry_launch(self) -> None:
        configure_logging(level="CRITICAL")
        import subprocess, time, urllib.request, socket

        def find_free_port() -> int:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", 0))
                return s.getsockname()[1]

        port = find_free_port()
        proc = subprocess.Popen(
            ["uv", "run", "python", "-m", "app.gateway_entry", "127.0.0.1", str(port)],
            cwd=str(Path.cwd()),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        try:
            deadline = time.monotonic() + 10
            ok = False
            while time.monotonic() < deadline:
                try:
                    resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1.0)
                    assert resp.status == 200
                    ok = True
                    break
                except Exception:
                    time.sleep(0.3)
            assert ok, "Gateway did not start in time"
            resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/docs", timeout=2.0)
            assert resp.status == 200
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
                proc.wait()


class TestProcessManagerEdgeCases:
    def test_read_output_thread(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(
            id="echo", name="Echo",
            command=[sys.executable, "-c", "print('hello from subprocess')"],
        ))
        pm.start("echo")
        time.sleep(0.5)
        pm.stop("echo")

    def test_start_file_not_found(self) -> None:
        configure_logging(level="CRITICAL")
        pm = ProcessManager()
        pm.add(ManagedProcess(id="bad", name="Bad", command=["nonexistent_command_xyz"]))
        assert pm.start("bad") is False

    def test_wait_for_all_ready_empty(self) -> None:
        pm = ProcessManager()
        assert pm.wait_for_all_ready(timeout=0.1) == {}
