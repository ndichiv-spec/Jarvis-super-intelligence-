from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_intelligence.tasks import Task, TaskGraph, TaskState
from jarvis_intelligence.executor import ExecutionEngine, ExecutionResult
from jarvis_intelligence.context import ExecutionContext
from jarvis_intelligence.decision import Decision, DecisionEngine, DecisionType
from jarvis_intelligence.telemetry import TelemetryEngine


@dataclass
class CoordinationReport:
    plan_id: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    running_tasks: int = 0
    pending_tasks: int = 0
    duration_seconds: float = 0.0
    decisions_made: int = 0
    decisions: list[dict[str, Any]] = field(default_factory=list)
    results: dict[str, ExecutionResult] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class CoordinatorEngine:
    def __init__(
        self,
        execution_engine: ExecutionEngine | None = None,
        decision_engine: DecisionEngine | None = None,
        telemetry: TelemetryEngine | None = None,
    ) -> None:
        self._executor = execution_engine or ExecutionEngine()
        self._decisions = decision_engine or DecisionEngine()
        self._telemetry = telemetry or TelemetryEngine()
        self._reports: dict[str, CoordinationReport] = {}

    async def coordinate(self, plan_id: str, graph: TaskGraph, context: ExecutionContext | None = None) -> CoordinationReport:
        started = datetime.now(UTC)
        report = CoordinationReport(plan_id=plan_id)
        tasks = graph.all()
        report.total_tasks = len(tasks)
        results: dict[str, ExecutionResult] = {}

        while True:
            ready = graph.get_ready_tasks()
            if not ready:
                break

            for task in ready:
                should_execute = self._decisions.decide(
                    DecisionType.EXECUTE_TASK,
                    {"task_id": task.id, "task_ready": True},
                )
                report.decisions_made += 1
                report.decisions.append({"task_id": task.id, "decision": should_execute.type.value, "confidence": should_execute.confidence})

                graph.update(task.id, state=TaskState.RUNNING)

                result = await self._executor.execute_task(task)
                results[task.id] = result

                if result.success:
                    graph.update(task.id, state=TaskState.COMPLETED, result=result.output)
                    report.completed_tasks += 1
                else:
                    retry_decision = self._decisions.decide(
                        DecisionType.RETRY_TASK,
                        {"task_id": task.id, "retry_count": task.retry_count, "max_retries": task.max_retries},
                    )
                    report.decisions_made += 1
                    if retry_decision.confidence >= 0.5:
                        graph.update(task.id, state=TaskState.RETRYING)
                        retry_result = await self._executor.execute_task(task)
                        results[task.id] = retry_result
                        if retry_result.success:
                            graph.update(task.id, state=TaskState.COMPLETED, result=retry_result.output)
                            report.completed_tasks += 1
                        else:
                            graph.update(task.id, state=TaskState.FAILED, error=retry_result.error)
                            report.failed_tasks += 1
                            report.errors.append(f"Task {task.id} failed: {retry_result.error}")
                    else:
                        graph.update(task.id, state=TaskState.FAILED, error=result.error)
                        report.failed_tasks += 1
                        report.errors.append(f"Task {task.id} failed: {result.error}")

        report.running_tasks = len(graph.get_by_state(TaskState.RUNNING))
        report.pending_tasks = len(graph.get_by_state(TaskState.PENDING))
        report.results = results
        report.duration_seconds = (datetime.now(UTC) - started).total_seconds()

        self._reports[plan_id] = report
        self._telemetry.record_execution(plan_id, report)
        return report

    def get_report(self, plan_id: str) -> CoordinationReport | None:
        return self._reports.get(plan_id)
