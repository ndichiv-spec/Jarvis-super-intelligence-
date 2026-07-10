from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_tools.models import ToolHealthReport, ToolStatus


@dataclass(slots=True)
class InMemoryHealthMonitor:
    _reports: dict[str, ToolHealthReport] = field(default_factory=dict)
    _execution_counts: dict[str, int] = field(default_factory=dict)
    _failure_counts: dict[str, int] = field(default_factory=dict)
    _total_times: dict[str, list[int]] = field(default_factory=dict)
    _last_execution: dict[str, datetime] = field(default_factory=dict)

    def record_execution(
        self,
        tool_identifier: str,
        duration_ms: int,
        success: bool,
    ) -> ToolHealthReport:
        now = datetime.now(UTC)
        self._execution_counts[tool_identifier] = self._execution_counts.get(tool_identifier, 0) + 1
        self._last_execution[tool_identifier] = now
        if not success:
            self._failure_counts[tool_identifier] = self._failure_counts.get(tool_identifier, 0) + 1
        if tool_identifier not in self._total_times:
            self._total_times[tool_identifier] = []
        self._total_times[tool_identifier].append(duration_ms)
        # Keep only last 100
        self._total_times[tool_identifier] = self._total_times[tool_identifier][-100:]
        return self._build_report(tool_identifier)

    def record_failure(
        self,
        tool_identifier: str,
        error_message: str,
    ) -> ToolHealthReport:
        _ = error_message
        return self.record_execution(tool_identifier, 0, False)

    def get_report(self, tool_identifier: str) -> ToolHealthReport | None:
        return self._reports.get(tool_identifier)

    def list_reports(self) -> tuple[ToolHealthReport, ...]:
        return tuple(self._reports.values())

    def list_unhealthy(self) -> tuple[ToolHealthReport, ...]:
        return tuple(
            r
            for r in self._reports.values()
            if r.status != ToolStatus.ACTIVE or r.failure_count > r.execution_count * 0.3
        )

    def _build_report(self, tool_identifier: str) -> ToolHealthReport:
        count = self._execution_counts.get(tool_identifier, 0)
        failures = self._failure_counts.get(tool_identifier, 0)
        times = self._total_times.get(tool_identifier, [])
        avg_time = sum(times) / len(times) if times else 0.0
        last = self._last_execution.get(tool_identifier)
        failure_rate = failures / count if count else 0.0
        if failure_rate > 0.5:
            status = ToolStatus.FAILED
        elif failure_rate > 0.3:
            status = ToolStatus.UNDER_MAINTENANCE
        else:
            status = ToolStatus.ACTIVE
        report = ToolHealthReport(
            tool_identifier=tool_identifier,
            available=status == ToolStatus.ACTIVE,
            execution_count=count,
            failure_count=failures,
            average_execution_time_ms=avg_time,
            last_execution=last,
            status=status,
        )
        self._reports[tool_identifier] = report
        return report
