from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_brain.interfaces import ExecutionTimeline, MetricsCollector, StructuredLogger, Tracer
from jarvis_brain.models import BrainExecutionState


class NullStructuredLogger(StructuredLogger):
    def log(self, level: str, event: str, data: dict[str, object]) -> None:
        _ = (level, event, data)


class NullTracer(Tracer):
    def start_span(self, trace_id: str, name: str, attributes: dict[str, object]) -> None:
        _ = (trace_id, name, attributes)


class NullMetricsCollector(MetricsCollector):
    def increment(self, metric: str, value: int = 1) -> None:
        _ = (metric, value)

    def observe(self, metric: str, value: float) -> None:
        _ = (metric, value)


class NullExecutionTimeline(ExecutionTimeline):
    def record(self, state: BrainExecutionState) -> None:
        _ = state


@dataclass(slots=True)
class InMemoryExecutionTimeline(ExecutionTimeline):
    snapshots: list[BrainExecutionState] = field(default_factory=list)

    def record(self, state: BrainExecutionState) -> None:
        self.snapshots.append(state)
