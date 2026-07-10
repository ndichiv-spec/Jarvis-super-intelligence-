from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_agents.models import (
    AgentMetadata,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
    TaskPriority,
    TaskStatus,
)
from jarvis_agents.registry import InMemoryAgentRegistry
from jarvis_agents.tasks import InMemoryTaskManager


@dataclass(frozen=True, slots=True)
class Delegation:
    delegation_id: str
    parent_task_id: str
    subtask_ids: tuple[str, ...]
    strategy: str
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class TaskDelegator:
    _registry: InMemoryAgentRegistry
    _task_manager: InMemoryTaskManager
    _delegations: dict[str, Delegation] = field(default_factory=dict)

    def delegate(
        self,
        parent_task: AgentTask,
        subtasks: tuple[tuple[str, str], ...],
        strategy: str = "sequential",
    ) -> Delegation:
        subtask_ids: list[str] = []
        for description, target_role in subtasks:
            agent = self._find_agent_by_role(target_role)
            if agent is None:
                continue
            sub = AgentTask(
                task_id=f"sub-{uuid4().hex[:8]}",
                description=description,
                assigned_agent_id=agent.identifier,
                priority=parent_task.priority,
                dependencies=(parent_task.task_id,),
            )
            self._task_manager.create_task(sub)
            subtask_ids.append(sub.task_id)
        delegation = Delegation(
            delegation_id=f"del-{uuid4().hex[:8]}",
            parent_task_id=parent_task.task_id,
            subtask_ids=tuple(subtask_ids),
            strategy=strategy,
        )
        self._delegations[delegation.delegation_id] = delegation
        try:
            self._task_manager.create_task(parent_task)
        except (KeyError, ValueError):
            pass
        try:
            self._task_manager.assign_task(parent_task.task_id, "delegator")
        except KeyError:
            pass
        return delegation

    def get_delegation(self, delegation_id: str) -> Delegation | None:
        return self._delegations.get(delegation_id)

    def list_delegations(self) -> tuple[Delegation, ...]:
        return tuple(self._delegations.values())

    def complete_subtask(self, subtask_id: str, result: AgentTaskResult) -> bool:
        try:
            self._task_manager.complete_task(subtask_id, result)
        except KeyError:
            return False
        for delegation in list(self._delegations.values()):
            if subtask_id in delegation.subtask_ids:
                all_complete = all(
                    t.status == TaskStatus.COMPLETED
                    for t in (self._task_manager.get_task(sid) for sid in delegation.subtask_ids)
                    if t is not None
                )
                if all_complete:
                    parent_result = AgentTaskResult(
                        success=True,
                        output=f"All {len(delegation.subtask_ids)} subtasks completed",
                    )
                    try:
                        self._task_manager.complete_task(delegation.parent_task_id, parent_result)
                    except KeyError:
                        pass
                    updated = Delegation(
                        delegation_id=delegation.delegation_id,
                        parent_task_id=delegation.parent_task_id,
                        subtask_ids=delegation.subtask_ids,
                        strategy=delegation.strategy,
                        status="completed",
                        created_at=delegation.created_at,
                        updated_at=datetime.now(UTC),
                    )
                    self._delegations[delegation.delegation_id] = updated
                return True
        return True

    def fail_subtask(self, subtask_id: str, error: str) -> bool:
        try:
            self._task_manager.fail_task(subtask_id, error)
        except KeyError:
            return False
        for delegation in list(self._delegations.values()):
            if subtask_id in delegation.subtask_ids:
                updated = Delegation(
                    delegation_id=delegation.delegation_id,
                    parent_task_id=delegation.parent_task_id,
                    subtask_ids=delegation.subtask_ids,
                    strategy=delegation.strategy,
                    status="failed",
                    created_at=delegation.created_at,
                    updated_at=datetime.now(UTC),
                )
                self._delegations[delegation.delegation_id] = updated
                return True
        return True

    def _find_agent_by_role(self, role: str) -> AgentMetadata | None:
        agents = self._registry.list_by_status(AgentStatus.READY)
        for a in agents:
            if a.role == role:
                return a
        return None

    def delegation_status(self, delegation_id: str) -> dict[str, object] | None:
        delegation = self._delegations.get(delegation_id)
        if delegation is None:
            return None
        subtask_results: list[dict[str, object]] = []
        for sid in delegation.subtask_ids:
            task = self._task_manager.get_task(sid)
            if task is not None:
                subtask_results.append({
                    "task_id": sid,
                    "status": task.status.value,
                    "success": task.result.success if task.result else None,
                })
        return {
            "delegation_id": delegation_id,
            "status": delegation.status,
            "strategy": delegation.strategy,
            "subtask_count": len(delegation.subtask_ids),
            "subtasks": subtask_results,
        }
