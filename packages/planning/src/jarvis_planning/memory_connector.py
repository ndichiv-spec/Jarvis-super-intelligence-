from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from jarvis_memory.kernel import MemoryKernel
from jarvis_memory.models import (
    MemoryMetadata,
    MemoryPrivacyLevel,
    MemoryRecord,
    MemoryRelationship,
    MemoryRelationshipType,
    MemoryType,
    MemoryVisibility,
    RetrievalQuery,
    ScoredMemory,
)

from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task
from jarvis_planning.executor import Executor

if TYPE_CHECKING:
    from jarvis_planning.planner import Plan


@dataclass
class PlanMemoryRecord:
    plan_id: str
    objective: str
    goal: Goal | None
    tasks: list[Task]
    status: str
    created_at: datetime
    completed_at: datetime | None
    execution_summary: dict[str, Any] = field(default_factory=dict)
    outcome: str = ""
    lessons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "objective": self.objective,
            "goal": self.goal.to_dict() if self.goal else None,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_summary": self.execution_summary,
            "outcome": self.outcome,
            "lessons": self.lessons,
        }


_EXECUTION_SUMMARY_FIELDS = [
    "total_tasks", "completed_tasks", "successful_tasks",
    "failed_tasks", "total_duration_seconds", "overall_result",
]


class MemoryConnector:
    def __init__(self, memory_kernel: MemoryKernel | None = None) -> None:
        self._kernel = memory_kernel

    @property
    def kernel(self) -> MemoryKernel | None:
        return self._kernel

    def store_plan(self, plan: Plan, namespace: str = "planning") -> MemoryRecord:
        if self._kernel is None:
            return self._create_fallback_record(plan)

        content = plan.to_dict()
        metadata = self._build_metadata(
            identifier=f"plan-{plan.id}",
            tags=["planning", "plan", plan.status, plan.goal.category if plan.goal else "uncategorized"],
            source="planning_engine",
        )
        record = MemoryRecord(
            metadata=metadata,
            content=str(content),
            memory_type=MemoryType.PROCEDURAL,
        )
        return self._kernel.store(record)

    def store_execution_result(
        self, plan: Plan, executor: Executor, namespace: str = "planning"
    ) -> MemoryRecord:
        if self._kernel is None:
            return self._create_fallback_record(plan)

        results = executor.get_all_results()
        success_count = sum(1 for r in results.values() if r.success)
        fail_count = sum(1 for r in results.values() if not r.success)
        total_duration = sum(r.duration_seconds for r in results.values() if r.duration_seconds)

        execution_summary = {
            "total_tasks": len(results),
            "completed_tasks": success_count + fail_count,
            "successful_tasks": success_count,
            "failed_tasks": fail_count,
            "total_duration_seconds": total_duration,
            "overall_result": "success" if fail_count == 0 else "partial_failure",
        }

        tags = ["planning", "execution", plan.status]
        if fail_count == 0:
            tags.append("success")
        else:
            tags.append("has_failures")

        content = {
            "plan_id": plan.id,
            "objective": plan.objective,
            "status": plan.status,
            "execution_summary": execution_summary,
            "results": {tid: r.to_dict() for tid, r in results.items()},
        }

        metadata = self._build_metadata(
            identifier=f"exec-{plan.id}",
            tags=tags,
            source="planning_engine.executor",
        )
        record = MemoryRecord(
            metadata=metadata,
            content=str(content),
            memory_type=MemoryType.PROCEDURAL,
        )
        return self._kernel.store(record)

    def retrieve_similar_plans(self, objective: str, namespace: str = "planning") -> list[MemoryRecord]:
        if self._kernel is None:
            return []

        query = RetrievalQuery(
            context=objective,
            tags=frozenset(["planning"]),
        )
        results = self._kernel.retrieve(query)
        return [sm.memory for sm in results]

    def _build_metadata(
        self, identifier: str, tags: list[str], source: str
    ) -> MemoryMetadata:
        now = datetime.now(UTC)
        return MemoryMetadata(
            identifier=identifier,
            created_at=now,
            updated_at=now,
            confidence=1.0,
            importance=0.5,
            source=source,
            visibility=MemoryVisibility.SYSTEM,
            privacy_level=MemoryPrivacyLevel.MEDIUM,
            relationships=(),
            classification=MemoryType.PROCEDURAL,
            tags=frozenset(tags),
        )

    def _create_fallback_record(self, plan: Plan) -> MemoryRecord:
        metadata = self._build_metadata(
            identifier=f"plan-{plan.id}",
            tags=["planning", "plan"],
            source="planning_engine",
        )
        return MemoryRecord(
            metadata=metadata,
            content=str(plan.to_dict()),
            memory_type=MemoryType.PROCEDURAL,
        )
