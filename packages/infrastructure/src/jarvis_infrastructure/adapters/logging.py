from __future__ import annotations

import json
import logging as py_logging
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    correlation_id: str = ""
    execution_id: str = ""
    source: str = ""


class Logger(Protocol):
    def debug(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

    def info(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

    def warning(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

    def error(self, message: str, *, context: ExecutionContext | None = None) -> None: ...

class TelemetryLogExporter(Protocol):
    def emit(self, payload: Mapping[str, Any]) -> None: ...


class _StructuredLoggerAdapter(BaseInfrastructureAdapter, Logger):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        logger: py_logging.Logger,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("logging", "structured"),
                configuration_profile="default",
                compatibility=("logger:v1",),
            )
        )
        self._logger = logger

    def debug(self, message: str, *, context: ExecutionContext | None = None) -> None:
        self._logger.debug(self._format_message("DEBUG", message, context))

    def info(self, message: str, *, context: ExecutionContext | None = None) -> None:
        self._logger.info(self._format_message("INFO", message, context))

    def warning(self, message: str, *, context: ExecutionContext | None = None) -> None:
        self._logger.warning(self._format_message("WARNING", message, context))

    def error(self, message: str, *, context: ExecutionContext | None = None) -> None:
        self._logger.error(self._format_message("ERROR", message, context))

    @staticmethod
    def _format_message(level: str, message: str, context: ExecutionContext | None) -> str:
        payload: dict[str, Any] = {"level": level, "message": message}
        if context is not None:
            payload["correlation_id"] = context.correlation_id
            payload["execution_id"] = context.execution_id
            payload["source"] = context.source
        return json.dumps(payload, sort_keys=True)


class ConsoleLoggerAdapter(_StructuredLoggerAdapter):
    def __init__(self, *, logger_name: str = "jarvis.infrastructure.console") -> None:
        logger = py_logging.getLogger(logger_name)
        logger.setLevel(py_logging.INFO)
        if not logger.handlers:
            handler = py_logging.StreamHandler()
            logger.addHandler(handler)
        super().__init__(
            identifier="logging.console",
            provider="console",
            logger=logger,
        )


class FileLoggerAdapter(_StructuredLoggerAdapter):
    def __init__(self, *, file_path: str = "logs/jarvis-infrastructure.log") -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger = py_logging.getLogger("jarvis.infrastructure.file")
        logger.setLevel(py_logging.INFO)
        if not logger.handlers:
            handler = py_logging.FileHandler(path, encoding="utf-8")
            logger.addHandler(handler)
        super().__init__(
            identifier="logging.file",
            provider="file",
            logger=logger,
        )


class OpenTelemetryLoggerAdapter(_StructuredLoggerAdapter):
    def __init__(
        self,
        *,
        exporter: TelemetryLogExporter | None = None,
        logger_name: str = "jarvis.infrastructure.otel",
    ) -> None:
        self._exporter = exporter
        logger = py_logging.getLogger(logger_name)
        logger.setLevel(py_logging.INFO)
        if not logger.handlers:
            handler = py_logging.StreamHandler()
            logger.addHandler(handler)
        super().__init__(
            identifier="logging.opentelemetry",
            provider="opentelemetry",
            logger=logger,
        )

    def info(self, message: str, *, context: ExecutionContext | None = None) -> None:
        super().info(message, context=context)
        if self._exporter is not None:
            payload: dict[str, Any] = {"message": message, "severity": "INFO"}
            if context is not None:
                payload["correlation_id"] = context.correlation_id
                payload["execution_id"] = context.execution_id
            self._exporter.emit(payload)
