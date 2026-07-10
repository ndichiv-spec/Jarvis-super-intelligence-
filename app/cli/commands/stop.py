"""STOP command — graceful platform shutdown."""

from __future__ import annotations

import argparse

from app.process_manager import ProcessManager
from app.runtime import Runtime


def cmd_stop(args: argparse.Namespace, runtime: Runtime) -> int:
    runtime.stop()
    results = ProcessManager.kill_stale_processes()
    killed = [k for k, v in results.items() if v]
    if killed:
        print(f"Killed stale processes: {', '.join(killed)}")
    print("Platform stopped")
    return 0
