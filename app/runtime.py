"""Runtime — facade that wraps bootstrap, kernel, and CLI access."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.banner import print_banner
from app.bootstrap import BootstrapContext, bootstrap
from app.browser import open_browser
from app.configuration import AppConfig
from app.diagnostics import DiagnosticReport, generate_report
from app.kernel import AppKernel, KernelState
from app.log import get_logger
from app.process_manager import ManagedProcess, ProcessManager
from app.registry import ServiceRegistry


def _resolve_npm() -> list[str]:
    npm = shutil.which("npm")
    if npm:
        return [npm]
    npm_cmd = shutil.which("npm.cmd")
    if npm_cmd:
        return [npm_cmd]
    return ["npm"]


class Runtime:
    def __init__(self) -> None:
        self._context: BootstrapContext | None = None
        self._process_manager = ProcessManager()
        self._logger = get_logger("runtime")

    @property
    def kernel(self) -> AppKernel | None:
        if self._context is None:
            return None
        return self._context.kernel

    @property
    def config(self) -> AppConfig | None:
        if self.kernel is None:
            return None
        return self.kernel.config

    @property
    def registry(self) -> ServiceRegistry | None:
        if self.kernel is None:
            return None
        return self.kernel.registry

    @property
    def state(self) -> KernelState | None:
        if self.kernel is None:
            return None
        return self.kernel.state

    @property
    def process_manager(self) -> ProcessManager:
        return self._process_manager

    def start(self, config_path: str = "", start_apps: bool = True) -> AppKernel:
        self._context = bootstrap(config_path)
        kernel = self._context.kernel
        cfg = kernel.config

        if not start_apps:
            return kernel

        from datetime import UTC, datetime
        elapsed_start = datetime.now(UTC)
        root_dir = Path.cwd()

        self._logger.info("Launching Gateway...")
        self._process_manager.add(ManagedProcess(
            id="gateway",
            name="JARVIS Gateway",
            command=["uv", "run", "python", "-m", "app.gateway_entry", cfg.gateway_host, str(cfg.gateway_port)],
            cwd=str(root_dir),
            host="127.0.0.1",
            port=cfg.gateway_port,
            health_path="/health",
        ))
        gateway_started = self._process_manager.start("gateway")

        self._logger.info("Launching Home...")
        home_dir = str(root_dir / "packages" / "home")
        npm_cmd = _resolve_npm()
        self._process_manager.add(ManagedProcess(
            id="home",
            name="JARVIS Home",
            command=npm_cmd + ["run", "dev"],
            cwd=home_dir,
            host="127.0.0.1",
            port=3000,
            health_path="/",
            max_restarts=0,
        ))
        home_started = self._process_manager.start("home")

        if not gateway_started or not home_started:
            kernel.fail("Failed to launch application processes")
            self._logger.error("Failed to launch application processes")
            ph = self._process_manager.health_report()
            print_banner(kernel, 0.0, ph)
            return kernel

        self._logger.info("Waiting for Gateway and Home to be ready...")
        results = self._process_manager.wait_for_all_ready(timeout=60.0)
        ph = self._process_manager.health_report()

        if results.get("gateway") and results.get("home"):
            kernel.mark_ready()
            self._logger.info("All application processes ready")
            from app.shutdown import install_signal_handlers
            install_signal_handlers(kernel, self._process_manager)
            open_browser(cfg.home_url, enabled=(cfg.profile == "development"))
        else:
            failures = [k for k, v in results.items() if not v]
            kernel.mark_degraded(f"Process(es) not ready: {', '.join(failures)}")
            self._logger.warning("Process(es) not ready: %s", ', '.join(failures))

        elapsed = (datetime.now(UTC) - elapsed_start).total_seconds()
        print_banner(kernel, elapsed, ph)
        return kernel

    def stop(self) -> None:
        if self._context:
            from app.shutdown import run_shutdown
            run_shutdown(self._context.kernel, self._process_manager)
            self._context = None

    def restart(self, config_path: str = "", start_apps: bool = True) -> AppKernel:
        self.stop()
        return self.start(config_path, start_apps=start_apps)

    def health(self) -> dict:
        if self.kernel is None:
            return {"platform": "not_running", "summary": "", "checks": [], "processes": {}, "process_checks": []}
        report = self.kernel.get_health_report()
        ph = self._process_manager.health_report()
        process_checks = []
        for pid, info in ph.items():
            process_checks.append({
                "subsystem": pid,
                "status": "ready" if info.get("healthy") else ("error" if info.get("alive") is False else "unknown"),
                "message": f"PID {info['pid']}, port {info['port']}, uptime {info['uptime']}" if info.get("pid") else "Not running",
            })
        return {
            "platform": report.platform.value,
            "summary": report.summary,
            "checks": [{"subsystem": c.subsystem, "status": c.status.value, "message": c.message} for c in report.checks],
            "processes": ph,
            "process_checks": process_checks,
        }

    def status(self) -> dict:
        if self.kernel is None:
            return {"status": "not_running"}
        ph = self._process_manager.health_report()
        return {
            "status": self.kernel.lifecycle.state.value,
            "services": self.kernel.registry.count(),
            "version": self.kernel.state.version,
            "processes": ph,
        }

    def diagnostics(self) -> DiagnosticReport:
        if self.kernel is None:
            raise RuntimeError("Platform not running")
        return generate_report(self.kernel)
