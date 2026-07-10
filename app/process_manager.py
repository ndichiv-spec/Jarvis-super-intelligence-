"""Process Manager — supervise child processes with health checks and auto-restart."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Thread
from typing import Any

from app.log import get_logger


def _pid_dir() -> Path:
    return Path.cwd() / ".jarvis"


def _pid_file(proc_id: str) -> Path:
    return _pid_dir() / f"{proc_id}.pid"


def write_pid_file(proc_id: str, pid: int) -> None:
    d = _pid_dir()
    d.mkdir(parents=True, exist_ok=True)
    _pid_file(proc_id).write_text(str(pid))


def read_pid_file(proc_id: str) -> int | None:
    f = _pid_file(proc_id)
    if f.exists():
        try:
            return int(f.read_text().strip())
        except (ValueError, OSError):
            return None
    return None


def remove_pid_file(proc_id: str) -> None:
    _pid_file(proc_id).unlink(missing_ok=True)


@dataclass
class ManagedProcess:
    id: str
    name: str
    command: list[str]
    cwd: str | None = None
    env: dict[str, str] | None = None
    host: str = "127.0.0.1"
    port: int = 0
    health_path: str = "/"
    max_restarts: int = 3
    process: subprocess.Popen | None = None
    started_at: datetime | None = None
    restarts: int = 0


class ProcessManager:
    def __init__(self) -> None:
        self._processes: dict[str, ManagedProcess] = {}
        self._logger = get_logger("procman")

    def add(self, proc: ManagedProcess) -> None:
        self._processes[proc.id] = proc

    def start(self, proc_id: str) -> bool:
        proc = self._processes.get(proc_id)
        if proc is None:
            self._logger.error("[%s] Unknown process", proc_id)
            return False
        if proc.process is not None and proc.process.poll() is None:
            return True
        env = os.environ.copy()
        if proc.env:
            env.update(proc.env)
        try:
            proc.process = subprocess.Popen(
                proc.command,
                cwd=proc.cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            proc.started_at = datetime.now(UTC)
            self._logger.info("[%s] Started (PID %d)", proc_id, proc.process.pid)
            write_pid_file(proc_id, proc.process.pid)
            Thread(target=self._read_output, args=(proc_id,), daemon=True).start()
            return True
        except FileNotFoundError:
            self._logger.error("[%s] Command not found: %s", proc_id, proc.command[0] if proc.command else "?")
            return False
        except Exception as e:
            self._logger.error("[%s] Failed to start: %s", proc_id, e)
            return False

    def _read_output(self, proc_id: str) -> None:
        proc = self._processes.get(proc_id)
        if proc is None or proc.process is None or proc.process.stdout is None:
            return
        for line in proc.process.stdout:
            line = line.rstrip("\r\n")
            if line:
                self._logger.info("[%s] %s", proc_id, line)

    def stop(self, proc_id: str, timeout: float = 5.0) -> bool:
        proc = self._processes.get(proc_id)
        if proc is None:
            return True
        if proc.process is None or proc.process.poll() is not None:
            return True
        pid = proc.process.pid
        self._logger.info("[%s] Stopping (PID %d)...", proc_id, pid)
        try:
            proc.process.terminate()
            proc.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._logger.warning("[%s] Force killing (PID %d)", proc_id, pid)
            proc.process.kill()
            proc.process.wait()
        self._logger.info("[%s] Stopped", proc_id)
        remove_pid_file(proc_id)
        return True

    def stop_all(self, timeout: float = 5.0) -> None:
        for proc_id in list(self._processes):
            self.stop(proc_id, timeout)

    @staticmethod
    def kill_stale_processes(proc_ids: list[str] | None = None, timeout: float = 5.0) -> dict[str, bool]:
        logger = get_logger("procman")
        target_ids = proc_ids or []
        if not target_ids:
            if _pid_dir().exists():
                for f in _pid_dir().iterdir():
                    if f.suffix == ".pid":
                        target_ids.append(f.stem)
        results: dict[str, bool] = {}
        for proc_id in target_ids:
            pid = read_pid_file(proc_id)
            if pid is None:
                results[proc_id] = True
                continue
            try:
                logger.info("[%s] Killing stale PID %d", proc_id, pid)
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    capture_output=True, timeout=timeout,
                )
                remove_pid_file(proc_id)
                logger.info("[%s] Killed stale PID %d", proc_id, pid)
                results[proc_id] = True
            except Exception as e:
                logger.error("[%s] Failed to kill stale PID %d: %s", proc_id, pid, e)
                results[proc_id] = False
        return results

    def is_alive(self, proc_id: str) -> bool:
        proc = self._processes.get(proc_id)
        if proc is None or proc.process is None:
            return False
        return proc.process.poll() is None

    def is_healthy(self, proc_id: str, timeout: float = 3.0) -> bool:
        proc = self._processes.get(proc_id)
        if proc is None or proc.process is None or proc.process.poll() is not None:
            return False
        if proc.port == 0:
            return proc.process.poll() is None
        return self._check_http(proc, timeout)

    @staticmethod
    def _check_http(proc: ManagedProcess, timeout: float = 3.0) -> bool:
        url = f"http://{proc.host}:{proc.port}{proc.health_path}"
        try:
            resp = urllib.request.urlopen(url, timeout=timeout)
            return resp.status < 500
        except (urllib.error.URLError, OSError, ValueError):
            return False

    def wait_for_ready(self, proc_id: str, timeout: float = 30.0, interval: float = 0.5) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.is_healthy(proc_id, timeout=max(1.0, timeout * 0.1)):
                return True
            time.sleep(interval)
        return False

    def wait_for_all_ready(self, timeout: float = 30.0) -> dict[str, bool]:
        return {pid: self.wait_for_ready(pid, timeout) for pid in self._processes}

    def health_report(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for proc_id, proc in self._processes.items():
            alive = self.is_alive(proc_id)
            healthy = self.is_healthy(proc_id) if alive else False
            pid = proc.process.pid if proc.process is not None and proc.process.poll() is None else None
            uptime = ""
            if proc.started_at is not None and alive:
                delta = datetime.now(UTC) - proc.started_at
                mins, secs = divmod(delta.seconds, 60)
                uptime = f"{mins}m{secs}s" if mins else f"{secs}s"
            result[proc_id] = {
                "pid": pid,
                "port": proc.port,
                "alive": alive,
                "healthy": healthy,
                "restarts": proc.restarts,
                "uptime": uptime,
            }
        return result

    def __enter__(self) -> ProcessManager:
        return self

    def __exit__(self, *args: object) -> None:
        self.stop_all()
