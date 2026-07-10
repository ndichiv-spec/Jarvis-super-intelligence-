"""RESTART command — stop then start the platform."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_restart(args: argparse.Namespace, runtime: Runtime) -> int:
    start_apps = not getattr(args, "no_apps", False)
    runtime.restart(args.config, start_apps=start_apps)
    print("Platform restarted successfully")
    print(f"  Status: {runtime.status()['status']}")
    print(f"  Services: {runtime.status()['services']}")
    return 0
