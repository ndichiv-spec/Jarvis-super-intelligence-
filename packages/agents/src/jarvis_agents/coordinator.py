from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_agents.models import (
    AgentGoal,
    AgentMetadata,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
    GoalStatus,
    TaskPriority,
    TaskStatus,
)
from jarvis_agents.registry import InMemoryAgentRegistry
from jarvis_agents.tasks import InMemoryTaskManager


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    step_id: str
    agent_role: str
    task_description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    status: str = "pending"


@dataclass(frozen=True, slots=True)
class Workflow:
    workflow_id: str
    name: str
    steps: tuple[WorkflowStep, ...]
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class InMemoryAgentCoordinator:
    _registry: InMemoryAgentRegistry
    _task_manager: InMemoryTaskManager
    _workflows: dict[str, Workflow] = field(default_factory=dict)
    _assignments: dict[str, str] = field(default_factory=dict)

    def create_workflow(
        self,
        name: str,
        steps: tuple[WorkflowStep, ...],
    ) -> Workflow:
        workflow = Workflow(
            workflow_id=f"wf-{uuid4().hex[:8]}",
            name=name,
            steps=steps,
        )
        self._workflows[workflow.workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> tuple[Workflow, ...]:
        return tuple(self._workflows.values())

    def start_workflow(self, workflow_id: str) -> Workflow | None:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return None
        updated = Workflow(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            steps=workflow.steps,
            status="running",
            created_at=workflow.created_at,
            updated_at=datetime.now(UTC),
        )
        self._workflows[workflow_id] = updated
        self._dispatch_ready_steps(workflow_id)
        return updated

    def _dispatch_ready_steps(self, workflow_id: str) -> None:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return
        for step in workflow.steps:
            if step.status != "pending":
                continue
            deps_met = all(
                any(
                    s.step_id == dep and s.status == "completed"
                    for s in workflow.steps
                )
                for dep in step.dependencies
            )
            if not deps_met:
                continue
            agent = self._find_agent_for_role(step.agent_role)
            if agent is None:
                continue
            task = AgentTask(
                task_id=f"task-{uuid4().hex[:8]}",
                description=step.task_description,
                assigned_agent_id=agent.identifier,
                priority=step.priority,
            )
            self._task_manager.create_task(task)
            self._assignments[step.step_id] = task.task_id

    def complete_step(self, step_id: str, result: AgentTaskResult) -> bool:
        task_id = self._assignments.get(step_id)
        if task_id is None:
            return False
        self._task_manager.complete_task(task_id, result)
        for wf in self._workflows.values():
            new_steps: list[WorkflowStep] = []
            for s in wf.steps:
                if s.step_id == step_id:
                    new_steps.append(WorkflowStep(
                        step_id=s.step_id,
                        agent_role=s.agent_role,
                        task_description=s.task_description,
                        priority=s.priority,
                        dependencies=s.dependencies,
                        status="completed",
                    ))
                else:
                    new_steps.append(s)
            updated = Workflow(
                workflow_id=wf.workflow_id,
                name=wf.name,
                steps=tuple(new_steps),
                status=wf.status,
                created_at=wf.created_at,
                updated_at=datetime.now(UTC),
            )
            self._workflows[wf.workflow_id] = updated
            self._dispatch_ready_steps(wf.workflow_id)
            self._check_workflow_completion(wf.workflow_id)
        return True

    def _find_agent_for_role(self, role: str) -> AgentMetadata | None:
        agents = self._registry.list_by_status(AgentStatus.READY)
        for a in agents:
            if a.role == role:
                return a
        return None

    def _check_workflow_completion(self, workflow_id: str) -> None:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return
        if all(s.status == "completed" for s in workflow.steps):
            updated = Workflow(
                workflow_id=workflow.workflow_id,
                name=workflow.name,
                steps=workflow.steps,
                status="completed",
                created_at=workflow.created_at,
                updated_at=datetime.now(UTC),
            )
            self._workflows[workflow_id] = updated
