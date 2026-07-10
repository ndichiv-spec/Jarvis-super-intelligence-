from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class MetricRecord:
    agent_id: str
    metric_name: str
    value: float
    tags: Mapping[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class MetricsCollector:
    _records: list[MetricRecord] = field(default_factory=list)
    _aggregates: dict[str, list[float]] = field(default_factory=dict)

    def record(
        self,
        agent_id: str,
        metric_name: str,
        value: float,
        tags: Mapping[str, str] | None = None,
    ) -> MetricRecord:
        record = MetricRecord(
            agent_id=agent_id,
            metric_name=metric_name,
            value=value,
            tags=tags or {},
        )
        self._records.append(record)
        key = f"{agent_id}:{metric_name}"
        if key not in self._aggregates:
            self._aggregates[key] = []
        self._aggregates[key].append(value)
        return record

    def record_task_duration(self, agent_id: str, duration_seconds: float) -> MetricRecord:
        return self.record(agent_id, "task_duration", duration_seconds, {"unit": "seconds"})

    def record_task_success(self, agent_id: str) -> MetricRecord:
        return self.record(agent_id, "task_success", 1.0)

    def record_task_failure(self, agent_id: str) -> MetricRecord:
        return self.record(agent_id, "task_failure", 1.0)

    def record_message_sent(self, agent_id: str) -> MetricRecord:
        return self.record(agent_id, "message_sent", 1.0)

    def record_message_received(self, agent_id: str) -> MetricRecord:
        return self.record(agent_id, "message_received", 1.0)

    def average(self, agent_id: str, metric_name: str) -> float | None:
        key = f"{agent_id}:{metric_name}"
        values = self._aggregates.get(key)
        if not values:
            return None
        return sum(values) / len(values)

    def count(self, agent_id: str, metric_name: str) -> int:
        key = f"{agent_id}:{metric_name}"
        return len(self._aggregates.get(key, []))

    def latest(self, agent_id: str, metric_name: str) -> MetricRecord | None:
        for record in reversed(self._records):
            if record.agent_id == agent_id and record.metric_name == metric_name:
                return record
        return None

    def query(
        self,
        agent_id: str | None = None,
        metric_name: str | None = None,
    ) -> tuple[MetricRecord, ...]:
        results = self._records
        if agent_id is not None:
            results = [r for r in results if r.agent_id == agent_id]
        if metric_name is not None:
            results = [r for r in results if r.metric_name == metric_name]
        return tuple(results)

    def summary(self, agent_id: str) -> dict[str, object]:
        metrics: dict[str, object] = {}
        for record in self._records:
            if record.agent_id != agent_id:
                continue
            name = record.metric_name
            key = f"{agent_id}:{name}"
            values = self._aggregates.get(key, [])
            if values:
                metrics[name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1],
                }
        return metrics

    def agent_summaries(self) -> dict[str, dict[str, object]]:
        agent_ids = set(r.agent_id for r in self._records)
        return {aid: self.summary(aid) for aid in agent_ids}

    def clear(self) -> None:
        self._records.clear()
        self._aggregates.clear()
