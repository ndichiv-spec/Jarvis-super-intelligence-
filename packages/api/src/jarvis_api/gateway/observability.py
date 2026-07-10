from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_api.gateway.protocols import ObservabilityProtocol


@dataclass(frozen=True, slots=True)
class StructuredLogEntry:
    timestamp: datetime
    level: str
    message: str
    context: Mapping[str, object] = field(default_factory=dict)


class InMemoryObservability(ObservabilityProtocol):
    def __init__(self) -> None:
        self._logs: list[StructuredLogEntry] = []
        self._counters: Counter[str] = Counter()
        self._latencies: dict[str, list[float]] = {}

    def log(self, level: str, message: str, *, context: Mapping[str, object] | None = None) -> None:
        self._logs.append(
            StructuredLogEntry(
                timestamp=datetime.now(tz=UTC),
                level=level,
                message=message,
                context=context or {},
            )
        )

    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None:
        del tags
        self._counters[metric_name] += 1

    def record_latency(
        self,
        metric_name: str,
        milliseconds: float,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        del tags
        latencies = self._latencies.setdefault(metric_name, [])
        latencies.append(milliseconds)

    def health(self) -> Mapping[str, object]:
        errors = self._counters.get("gateway.requests.error", 0)
        status = "healthy" if errors == 0 else "degraded"
        return {
            "status": status,
            "error_count": errors,
            "log_entries": len(self._logs),
            "generated_at": datetime.now(tz=UTC).isoformat(),
        }

    def stats(self) -> Mapping[str, object]:
        average_latencies = {
            name: (sum(values) / len(values) if values else 0.0)
            for name, values in self._latencies.items()
        }
        return {
            "counters": dict(self._counters),
            "average_latencies": average_latencies,
            "logs": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                    "context": dict(entry.context),
                }
                for entry in self._logs
            ],
        }
