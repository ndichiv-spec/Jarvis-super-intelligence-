"""VERSION command — display platform version information."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_version(args: argparse.Namespace, runtime: Runtime) -> int:
    print(f"JARVIS Platform {runtime.state.version if runtime.state else '2.0.0'}")
    return 0
