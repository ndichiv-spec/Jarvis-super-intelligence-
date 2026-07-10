"""Structured logging — console, file, with future OpenTelemetry support."""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime
from enum import StrEnum
from logging import LogRecord
from pathlib import Path


class LogFormat(StrEnum):
    text = "text"
    json = "json"


class StructuredFormatter(logging.Formatter):
    def __init__(self, fmt: str | None = None, use_json: bool = False) -> None:
        super().__init__(fmt)
        self._use_json = use_json

    def format(self, record: LogRecord) -> str:
        if self._use_json:
            import json
            return json.dumps({
                "timestamp": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "line": record.lineno,
            })
        return super().format(record)


def configure_logging(
    level: str = "info",
    log_file: str = "",
    log_format: str = "text",
) -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    use_json = log_format == "json"
    formatter = StructuredFormatter(fmt, use_json=use_json)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(console)
    if log_file:
        fpath = Path(log_file)
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(str(fpath), encoding="utf-8")
        fh.setFormatter(formatter)
        root.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
