"""CONFIG command — display current configuration."""

from __future__ import annotations

import argparse
import json

from app.runtime import Runtime


def cmd_config(args: argparse.Namespace, runtime: Runtime) -> int:
    if runtime.config is None:
        print("Platform not running — run 'jarvis start' first")
        return 1
    output = {
        "profile": runtime.config.profile,
        "debug": runtime.config.debug,
        "log_level": runtime.config.log_level,
        "log_file": runtime.config.log_file,
        "gateway_host": runtime.config.gateway_host,
        "gateway_port": runtime.config.gateway_port,
        "home_url": runtime.config.home_url,
        "database_url": runtime.config.database_url,
        "redis_url": runtime.config.redis_url,
        "secret_key_set": bool(runtime.config.secret_key and runtime.config.secret_key != "change-me-in-production"),
    }
    print(json.dumps(output, indent=2))
    if args.show_all:
        print(json.dumps(runtime.config.extra, indent=2))
    return 0
