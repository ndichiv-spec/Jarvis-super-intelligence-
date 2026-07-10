"""STATUS command — show platform and service status."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_status(args: argparse.Namespace, runtime: Runtime) -> int:
    info = runtime.status()
    print(f"Status: {info['status']}")
    print(f"Version: {info['version']}")
    print(f"Services: {info['services']}")
    if runtime.kernel:
        health = runtime.health()
        print(f"Health: {health['platform']}")
        if health.get("summary"):
            print(f"  {health['summary']}")
    return 0
