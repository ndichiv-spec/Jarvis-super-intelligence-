"""CLI dispatcher — route commands to implementations."""

from __future__ import annotations

import argparse
import sys

from app.runtime import Runtime


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jarvis", description="JARVIS AI Platform CLI")
    parser.add_argument("--config", default="", help="Path to config file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Start the platform")
    p_start.add_argument("--config", default="", help="Path to config file")
    p_start.add_argument("--no-apps", action="store_true", help=argparse.SUPPRESS)

    p_stop = sub.add_parser("stop", help="Stop the platform")

    p_restart = sub.add_parser("restart", help="Restart the platform")
    p_restart.add_argument("--config", default="", help="Path to config file")
    p_restart.add_argument("--no-apps", action="store_true", help=argparse.SUPPRESS)

    p_status = sub.add_parser("status", help="Show platform status")
    p_health = sub.add_parser("health", help="Show health report")
    p_version = sub.add_parser("version", help="Show version")
    p_config = sub.add_parser("config", help="Show configuration")
    p_config.add_argument("--show-all", action="store_true", help="Show all extra config")
    p_logs = sub.add_parser("logs", help="Show logs")
    p_logs.add_argument("--tail", "-n", type=int, default=50, help="Number of lines to show")
    p_doctor = sub.add_parser("doctor", help="Run diagnostics")
    p_test = sub.add_parser("test", help="Run platform self-test")
    return parser


_COMMAND_MAP: dict[str, str] = {
    "start": "app.cli.commands.start",
    "stop": "app.cli.commands.stop",
    "restart": "app.cli.commands.restart",
    "status": "app.cli.commands.status",
    "health": "app.cli.commands.health",
    "version": "app.cli.commands.version",
    "config": "app.cli.commands.config",
    "logs": "app.cli.commands.logs",
    "doctor": "app.cli.commands.doctor",
    "test": "app.cli.commands.test",
}


_runtime: Runtime | None = None


def main(argv: list[str] | None = None) -> int:
    global _runtime
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    import importlib
    mod_path = _COMMAND_MAP.get(args.command)
    if not mod_path:
        parser.print_help()
        return 1
    mod = importlib.import_module(mod_path)
    cmd_func = getattr(mod, f"cmd_{args.command}", None)
    if cmd_func is None:
        print(f"Command not implemented: {args.command}")
        return 1
    if _runtime is None:
        _runtime = Runtime()
    return cmd_func(args, _runtime)
