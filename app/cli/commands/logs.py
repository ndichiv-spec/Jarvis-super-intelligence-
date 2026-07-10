"""LOGS command — tail or inspect platform logs."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_logs(args: argparse.Namespace, runtime: Runtime) -> int:
    config = runtime.config
    if not config:
        print("Platform not running")
        return 1
    log_path = config.log_file or "jarvis.log"
    import os
    if not os.path.exists(log_path):
        print(f"Log file not found: {log_path}")
        return 1
    with open(log_path) as f:
        lines = f.readlines()
    tail = lines[-args.tail:] if args.tail > 0 else lines
    for line in tail:
        print(line.rstrip("\n"))
    return 0
