from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jarvis_planning.agent_assigner import AgentAssigner, AssignmentStrategy
from jarvis_planning.analyzer import Goal, GoalAnalyzer
from jarvis_planning.decomposer import Task, TaskDecomposer
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.events import Event, EventBus, EventType
from jarvis_planning.executor import Executor, TaskExecutorFunc
from jarvis_planning.explanation import Explanation, ExplanationEngine
from jarvis_planning.memory_connector import MemoryConnector
from jarvis_planning.monitor import ProgressMonitor
from jarvis_planning.policies import ExecutionPolicy
from jarvis_planning.reasoning import ReasoningEngine
from jarvis_planning.replanner import ReplanResult, Replanner
from jarvis_planning.scheduler import Scheduler
from jarvis_planning.validator import PlanValidator, ValidationResult


class PlanStatus:
    CREATED = "created"
    ANALYZED = "analyzed"
    DECOMPOSED = "decomposed"
    VALIDATED = "validated"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REPLANNED = "replanned"


@dataclass
class Plan:
    id: str
    objective: str
    status: str = PlanStatus.CREATED
    goal: Goal | None = None
    tasks: list[Task] = field(default_factory=list)
    graph: DependencyGraph | None = None
    scheduler: Scheduler | None = None
    validation: ValidationResult | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "objective": self.objective,
            "status": self.status,
            "goal": self.goal.to_dict() if self.goal else None,
            "tasks": [t.to_dict() for t in self.tasks],
            "graph": self.graph.to_dict() if self.graph else None,
            "validation": self.validation.to_dict() if self.validation else None,
            "scheduler": self.scheduler.to_dict() if self.scheduler else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


class Planner:
    def __init__(
        self,
        analyzer: GoalAnalyzer | None = None,
        decomposer: TaskDecomposer | None = None,
        validator: PlanValidator | None = None,
        reasoning: ReasoningEngine | None = None,
        explanation: ExplanationEngine | None = None,
        event_bus: EventBus | None = None,
        agent_assigner: AgentAssigner | None = None,
        memory_connector: MemoryConnector | None = None,
    ) -> None:
        self._analyzer = analyzer or GoalAnalyzer()
        self._decomposer = decomposer or TaskDecomposer()
        self._validator = validator or PlanValidator()
        self._reasoning = reasoning or ReasoningEngine()
        self._event_bus = event_bus or EventBus()
        self._explanation = explanation or ExplanationEngine(self._reasoning)
        self._agent_assigner = agent_assigner
        self._memory_connector = memory_connector
        self._plans: dict[str, Plan] = {}
        self._executors: dict[str, Executor] = {}
        self._monitors: dict[str, ProgressMonitor] = {}
        self._replanners: dict[str, Replanner] = {}
        self._assignments: dict[str, list[Any]] = {}

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    def create_plan(self, objective: str, templates: list[str] | None = None) -> Plan:
        plan_id = str(uuid4())
        plan = Plan(id=plan_id, objective=objective)
        self._plans[plan_id] = plan
        self._event_bus.emit(Event(EventType.PLAN_CREATED, plan_id, {"objective": objective}))
        return plan

    def analyze(self, plan_id: str) -> Plan:
        plan = self._get_plan(plan_id)
        plan.goal = self._analyzer.analyze(plan.objective)
        self._reasoning.analyze_goal(plan.goal)
        plan.validation = self._validator.validate_goal(plan.goal)
        plan.status = PlanStatus.ANALYZED
        plan.updated_at = datetime.now(UTC)
        return plan

    def decompose(self, plan_id: str, templates: list[str] | None = None) -> Plan:
        plan = self._get_plan(plan_id)
        if plan.goal is None:
            plan = self.analyze(plan_id)
        plan.tasks = self._decomposer.decompose(plan.goal, templates)
        self._reasoning.analyze_task_decomposition(plan.tasks)
        plan.graph = DependencyGraph()
        plan.graph.add_tasks(plan.tasks)
        plan.validation = self._validator.validate_tasks(plan.tasks)
        plan.status = PlanStatus.DECOMPOSED
        plan.updated_at = datetime.now(UTC)
        return plan

    def validate(self, plan_id: str) -> Plan:
        plan = self._get_plan(plan_id)
        if plan.graph is None:
            plan = self.decompose(plan_id)
        plan.validation = self._validator.validate_all(plan.goal, plan.graph)
        plan.status = PlanStatus.VALIDATED
        plan.updated_at = datetime.now(UTC)
        if plan.validation.valid:
            self._event_bus.emit(Event(EventType.PLAN_VALIDATED, plan_id, {}))
        else:
            self._event_bus.emit(Event(EventType.PLAN_INVALID, plan_id,
                                        {"issues": [i.to_dict() for i in plan.validation.issues]}))
        return plan

    def prepare_execution(self, plan_id: str, policy: ExecutionPolicy | None = None) -> Plan:
        plan = self._get_plan(plan_id)
        if plan.graph is None:
            plan = self.decompose(plan_id)
        plan.scheduler = Scheduler(plan.graph, policy)
        self._reasoning.analyze_dependency_graph(plan.graph, plan.scheduler)
        executor = Executor(plan.scheduler, self._event_bus)
        executor.set_plan_id(plan_id)
        self._executors[plan_id] = executor
        monitor = ProgressMonitor(plan.scheduler, executor, self._event_bus)
        monitor.start_monitoring(plan_id)
        self._monitors[plan_id] = monitor
        replanner = Replanner(plan.scheduler, executor, monitor, self._event_bus)
        replanner.set_plan_id(plan_id)
        self._replanners[plan_id] = replanner
        plan.status = PlanStatus.EXECUTING
        plan.updated_at = datetime.now(UTC)
        self._event_bus.emit(Event(EventType.PLAN_STARTED, plan_id, {}))
        return plan

    def execute_next(self, plan_id: str) -> Plan:
        executor = self._get_executor(plan_id)
        result = executor.execute_next()
        plan = self._get_plan(plan_id)
        if executor.is_complete():
            all_success = all(r.success for r in executor.get_all_results().values())
            plan.status = PlanStatus.COMPLETED if all_success else PlanStatus.FAILED
            if all_success:
                self._event_bus.emit(Event(EventType.PLAN_COMPLETED, plan_id, {}))
            else:
                self._event_bus.emit(Event(EventType.PLAN_FAILED, plan_id, {}))
        plan.updated_at = datetime.now(UTC)
        return plan

    def execute_all(self, plan_id: str, store_memory: bool = True) -> Plan:
        executor = self._get_executor(plan_id)
        while not executor.is_complete():
            executor.execute_next()
        plan = self._get_plan(plan_id)
        all_success = all(r.success for r in executor.get_all_results().values())
        plan.status = PlanStatus.COMPLETED if all_success else PlanStatus.FAILED
        if all_success:
            self._event_bus.emit(Event(EventType.PLAN_COMPLETED, plan_id, {}))
        else:
            self._event_bus.emit(Event(EventType.PLAN_FAILED, plan_id, {}))
        plan.updated_at = datetime.now(UTC)
        if store_memory:
            self.store_execution_to_memory(plan_id)
        return plan

    def replan(self, plan_id: str, reason: str, context: dict[str, Any] | None = None) -> ReplanResult:
        replanner = self._get_replanner(plan_id)
        result = replanner.replan(reason, context)
        plan = self._get_plan(plan_id)
        if result.has_changes:
            plan.status = PlanStatus.REPLANNED
            plan.updated_at = datetime.now(UTC)
        return result

    def assign_agents(
        self, plan_id: str, strategy: AssignmentStrategy | None = None
    ) -> list[Any]:
        plan = self._get_plan(plan_id)
        if self._agent_assigner is None:
            return []
        if strategy is not None:
            self._agent_assigner._strategy = strategy
        assignments = self._agent_assigner.assign_tasks(plan.tasks)
        self._assignments[plan_id] = assignments
        self._reasoning.analyze_task_decomposition(plan.tasks)
        self._event_bus.emit(Event(
            EventType.AGENT_ASSIGNED, plan_id,
            {"assignments": [a.to_dict() for a in assignments]},
        ))
        return assignments

    def store_to_memory(self, plan_id: str, namespace: str = "planning") -> Any:
        plan = self._get_plan(plan_id)
        if self._memory_connector is None:
            return None
        record = self._memory_connector.store_plan(plan, namespace)
        return record

    def store_execution_to_memory(self, plan_id: str, namespace: str = "planning") -> Any:
        plan = self._get_plan(plan_id)
        executor = self._executors.get(plan_id)
        if self._memory_connector is None or executor is None:
            return None
        return self._memory_connector.store_execution_result(plan, executor, namespace)

    def retrieve_similar_plans(self, objective: str, namespace: str = "planning") -> list[Any]:
        if self._memory_connector is None:
            return []
        return self._memory_connector.retrieve_similar_plans(objective, namespace)

    def register_executor(self, plan_id: str, task_type: str, func: TaskExecutorFunc) -> None:
        executor = self._get_executor(plan_id)
        executor.register_executor(task_type, func)

    def get_plan(self, plan_id: str) -> Plan | None:
        return self._plans.get(plan_id)

    def get_progress(self, plan_id: str) -> Any:
        monitor = self._monitors.get(plan_id)
        if monitor is None:
            return None
        return monitor.get_progress()

    def get_explanation(self, plan_id: str) -> Explanation:
        plan = self._get_plan(plan_id)
        if plan.scheduler and plan.graph and plan.goal:
            return self._explanation.generate_plan_summary(plan.goal, plan.graph, plan.scheduler)
        if plan.goal:
            return self._explanation.generate_goal_summary(plan.goal)
        return Explanation()

    def get_completion_summary(self, plan_id: str) -> Explanation:
        plan = self._get_plan(plan_id)
        executor = self._executors.get(plan_id)
        if executor and plan.goal and plan.graph:
            return self._explanation.generate_completion_summary(plan.goal, plan.graph, executor)
        return Explanation()

    def cancel_plan(self, plan_id: str) -> Plan:
        plan = self._get_plan(plan_id)
        plan.status = PlanStatus.CANCELLED
        plan.updated_at = datetime.now(UTC)
        self._event_bus.emit(Event(EventType.PLAN_CANCELLED, plan_id, {}))
        return plan

    def list_plans(self) -> list[dict[str, Any]]:
        return [{"id": p.id, "objective": p.objective, "status": p.status,
                 "created_at": p.created_at.isoformat()}
                for p in self._plans.values()]

    def full_plan(
        self, objective: str, templates: list[str] | None = None,
        assign_agents: bool = True, store_memory: bool = True,
    ) -> Plan:
        plan = self.create_plan(objective)
        plan = self.analyze(plan.id)
        plan = self.decompose(plan.id, templates)
        if assign_agents:
            self.assign_agents(plan.id)
        plan = self.validate(plan.id)
        plan = self.prepare_execution(plan.id)
        if store_memory:
            self.store_to_memory(plan.id)
        self._reasoning.analyze_schedule(plan.scheduler)
        self._event_bus.emit(Event(EventType.MILESTONE_REACHED, plan.id,
                                    {"milestone": "Plan fully constructed and ready for execution"}))
        return plan

    def _get_plan(self, plan_id: str) -> Plan:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise ValueError(f"Plan not found: {plan_id}")
        return plan

    def _get_executor(self, plan_id: str) -> Executor:
        executor = self._executors.get(plan_id)
        if executor is None:
            raise ValueError(f"Executor not found for plan: {plan_id}. Call prepare_execution first.")
        return executor

    def _get_replanner(self, plan_id: str) -> Replanner:
        replanner = self._replanners.get(plan_id)
        if replanner is None:
            raise ValueError(f"Replanner not found for plan: {plan_id}. Call prepare_execution first.")
        return replanner
