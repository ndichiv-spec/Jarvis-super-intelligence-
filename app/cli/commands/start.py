"""START command — bootstrap the platform."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_start(args: argparse.Namespace, runtime: Runtime) -> int:
    start_apps = not getattr(args, "no_apps", False)
    runtime.start(args.config, start_apps=start_apps)
    return 0
