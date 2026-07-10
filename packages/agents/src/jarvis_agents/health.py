from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_agents.models import AgentHealthReport, AgentStatus


@dataclass(slots=True)
class InMemoryHealthMonitor:
    _reports: dict[str, AgentHealthReport] = field(default_factory=dict)
    _heartbeat_timeout_seconds: int = 300

    def set_heartbeat_timeout(self, seconds: int) -> None:
        self._heartbeat_timeout_seconds = seconds

    def record_heartbeat(
        self,
        agent_id: str,
        status: AgentStatus,
        metadata: dict[str, str] | None = None,
    ) -> AgentHealthReport:
        now = datetime.now(UTC)
        existing = self._reports.get(agent_id)
        report = AgentHealthReport(
            agent_id=agent_id,
            status=status,
            available=status
            not in (
                AgentStatus.FAILED,
                AgentStatus.SUSPENDED,
                AgentStatus.RETIRED,
            ),
            heartbeat_timestamp=now,
            failure_count=existing.failure_count if existing else 0,
            last_failure_message=existing.last_failure_message if existing else None,
            performance_metadata=dict(metadata or {}),
            created_at=now,
        )
        self._reports[agent_id] = report
        return report

    def record_failure(self, agent_id: str, error_message: str) -> AgentHealthReport:
        now = datetime.now(UTC)
        existing = self._reports.get(agent_id)
        report = AgentHealthReport(
            agent_id=agent_id,
            status=AgentStatus.FAILED,
            available=False,
            heartbeat_timestamp=now,
            failure_count=(existing.failure_count + 1) if existing else 1,
            last_failure_message=error_message,
            created_at=now,
        )
        self._reports[agent_id] = report
        return report

    def get_report(self, agent_id: str) -> AgentHealthReport | None:
        return self._reports.get(agent_id)

    def list_reports(self) -> tuple[AgentHealthReport, ...]:
        return tuple(self._reports.values())

    def list_unhealthy(self) -> tuple[AgentHealthReport, ...]:
        now = datetime.now(UTC)
        results: list[AgentHealthReport] = []
        for report in self._reports.values():
            if not report.available:
                results.append(report)
                continue
            elapsed = (now - report.heartbeat_timestamp).total_seconds()
            if elapsed > self._heartbeat_timeout_seconds:
                results.append(report)
        return tuple(results)
