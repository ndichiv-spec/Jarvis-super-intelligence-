from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_automation.models import (
    MonitoringReport,
    WorkflowHealthReport,
    WorkflowStatus,
)


@dataclass(slots=True)
class InMemoryMonitoringEngine:
    _health: dict[str, WorkflowHealthReport] = field(default_factory=dict)
    _reports: dict[str, MonitoringReport] = field(default_factory=dict)
    _execution_counts: dict[str, int] = field(default_factory=dict)
    _success_counts: dict[str, int] = field(default_factory=dict)
    _failure_counts: dict[str, int] = field(default_factory=dict)
    _total_durations: dict[str, list[int]] = field(default_factory=dict)
    _last_execution: dict[str, datetime] = field(default_factory=dict)
    _last_error: dict[str, str] = field(default_factory=dict)

    def record_execution(
        self,
        workflow_id: str,
        execution_id: str,
        status: WorkflowStatus,
    ) -> MonitoringReport:
        now = datetime.now(UTC)
        self._execution_counts[workflow_id] = (
            self._execution_counts.get(workflow_id, 0) + 1
        )
        self._last_execution[workflow_id] = now
        if status == WorkflowStatus.COMPLETED:
            self._success_counts[workflow_id] = (
                self._success_counts.get(workflow_id, 0) + 1
            )
        elif status in (
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ):
            self._failure_counts[workflow_id] = (
                self._failure_counts.get(workflow_id, 0) + 1
            )
        report = MonitoringReport(
            report_id=f"report-{execution_id}",
            workflow_id=workflow_id,
            execution_id=execution_id,
            status=status,
            total_duration_ms=0,
            created_at=now,
        )
        self._reports[execution_id] = report
        self._build_health(workflow_id)
        return report

    def record_step_completion(
        self,
        execution_id: str,
        step_id: str,
        duration_ms: int,
        success: bool,
    ) -> None:
        report = self._reports.get(execution_id)
        if report is None:
            return
        durations = dict(report.step_duration_ms)
        durations[step_id] = duration_ms
        total = report.total_duration_ms + duration_ms
        updated = MonitoringReport(
            report_id=report.report_id,
            workflow_id=report.workflow_id,
            execution_id=report.execution_id,
            status=report.status,
            step_duration_ms=durations,
            total_duration_ms=total,
            retries=report.retries,
            failures=report.failures + (0 if success else 1),
            resource_usage=dict(report.resource_usage),
            created_at=report.created_at,
        )
        self._reports[execution_id] = updated

    def get_workflow_health(
        self, workflow_id: str,
    ) -> WorkflowHealthReport | None:
        return self._health.get(workflow_id)

    def list_health_reports(self) -> tuple[WorkflowHealthReport, ...]:
        return tuple(self._health.values())

    def list_unhealthy(self) -> tuple[WorkflowHealthReport, ...]:
        return tuple(
            r
            for r in self._health.values()
            if r.execution_count > 0
            and r.failure_count / r.execution_count > 0.3
        )

    def _build_health(self, workflow_id: str) -> None:
        count = self._execution_counts.get(workflow_id, 0)
        successes = self._success_counts.get(workflow_id, 0)
        failures = self._failure_counts.get(workflow_id, 0)
        total_duration = sum(
            self._total_durations.get(workflow_id, [0]),
        )
        avg = total_duration / count if count else 0.0
        report = WorkflowHealthReport(
            workflow_id=workflow_id,
            execution_count=count,
            success_count=successes,
            failure_count=failures,
            average_duration_ms=avg,
            last_execution=self._last_execution.get(workflow_id),
            last_error=self._last_error.get(workflow_id),
        )
        self._health[workflow_id] = report
