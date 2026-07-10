from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_intelligence.cognition import CognitionEngine, CognitionState
from jarvis_intelligence.reasoning import ReasoningEngine, ReasoningMode, ReasoningResult
from jarvis_intelligence.planner import IntelligencePlan, IntelligencePlanner
from jarvis_intelligence.executor import ExecutionEngine
from jarvis_intelligence.coordinator import CoordinatorEngine, CoordinationReport
from jarvis_intelligence.decision import Decision, DecisionEngine, DecisionType
from jarvis_intelligence.goals import Goal, GoalManager, GoalPriority, GoalState
from jarvis_intelligence.context import ContextManager, ExecutionContext
from jarvis_intelligence.strategies import Strategy, StrategyType
from jarvis_intelligence.tasks import Task, TaskGraph, TaskState
from jarvis_intelligence.evaluator import EvaluationEngine, EvaluationResult
from jarvis_intelligence.optimizer import OptimizerEngine
from jarvis_intelligence.learning import LearningEngine
from jarvis_intelligence.confidence import ConfidenceEngine
from jarvis_intelligence.priorities import PriorityEngine
from jarvis_intelligence.scheduler import SchedulerEngine
from jarvis_intelligence.policies import PolicyEngine, ExecutionPolicy
from jarvis_intelligence.safety import SafetyEngine
from jarvis_intelligence.telemetry import TelemetryEngine


@dataclass
class IntelligenceResult:
    goal: Goal
    plan: IntelligencePlan | None = None
    cognition: CognitionState | None = None
    reasoning: ReasoningResult | None = None
    decisions: list[Decision] = field(default_factory=list)
    coordination: CoordinationReport | None = None
    evaluations: list[EvaluationResult] = field(default_factory=list)
    success: bool = False
    error: str | None = None


class IntelligenceEngine:
    def __init__(
        self,
        cognition: CognitionEngine | None = None,
        reasoning: ReasoningEngine | None = None,
        planner: IntelligencePlanner | None = None,
        executor: ExecutionEngine | None = None,
        coordinator: CoordinatorEngine | None = None,
        decision: DecisionEngine | None = None,
        goal_manager: GoalManager | None = None,
        context_manager: ContextManager | None = None,
        evaluator: EvaluationEngine | None = None,
        optimizer: OptimizerEngine | None = None,
        learning: LearningEngine | None = None,
        confidence: ConfidenceEngine | None = None,
        priority: PriorityEngine | None = None,
        scheduler: SchedulerEngine | None = None,
        policy: PolicyEngine | None = None,
        safety: SafetyEngine | None = None,
        telemetry: TelemetryEngine | None = None,
    ) -> None:
        self._telemetry = telemetry or TelemetryEngine()
        self._cognition = cognition or CognitionEngine()
        self._reasoning = reasoning or ReasoningEngine()
        self._goal_manager = goal_manager or GoalManager()
        self._planner = planner or IntelligencePlanner(goal_manager=self._goal_manager)
        self._executor = executor or ExecutionEngine()
        self._coordinator = coordinator or CoordinatorEngine(telemetry=self._telemetry)
        self._decisions = decision or DecisionEngine()
        self._context_manager = context_manager or ContextManager()
        self._evaluator = evaluator or EvaluationEngine()
        self._optimizer = optimizer or OptimizerEngine()
        self._learning = learning or LearningEngine()
        self._confidence = confidence or ConfidenceEngine()
        self._priority = priority or PriorityEngine()
        self._scheduler = scheduler or SchedulerEngine()
        self._policy = policy or PolicyEngine()
        self._safety = safety or SafetyEngine()

    async def execute_goal(
        self,
        goal_description: str,
        priority: GoalPriority = GoalPriority.MEDIUM,
        policy: ExecutionPolicy = ExecutionPolicy.BALANCED,
        context: dict[str, Any] | None = None,
    ) -> IntelligenceResult:
        self._policy.set_policy(policy)
        ctx = self._context_manager.create(ExecutionContext())

        try:
            cognition = self._cognition.process(goal_description, context)
            self._context_manager.push_reasoning(ctx, "cognition", f"Understood: {cognition.understanding}", cognition.confidence)

            reasoning = self._reasoning.reason(
                context=cognition.understanding,
                mode=ReasoningMode.STRATEGIC,
            )
            self._context_manager.push_reasoning(ctx, "reasoning", reasoning.conclusion, reasoning.confidence)

            plan = self._planner.create_plan(
                goal_description=goal_description,
                priority=priority,
                capabilities=tuple(cognition.key_entities),
            )

            safety_checks = self._safety.validate_goal(plan.goal)

            decompose_decision = self._decisions.decide(
                DecisionType.SELECT_STRATEGY,
                {"goal_id": plan.goal.id, "complexity": cognition.complexity},
            )

            plan = self._planner.decompose_goal(plan.id) or plan

            task_safety = self._safety.validate_task_graph(plan.task_graph)
            if any(not c.passed and c.severity == "critical" for c in task_safety):
                return IntelligenceResult(
                    goal=plan.goal,
                    plan=plan,
                    cognition=cognition,
                    reasoning=reasoning,
                    success=False,
                    error="Safety validation failed with critical issues",
                )

            report = await self._coordinator.coordinate(plan.id, plan.task_graph, ctx)

            evaluations: list[EvaluationResult] = []
            for task in plan.task_graph.all():
                result = report.results.get(task.id)
                eval_result = self._evaluator.evaluate(
                    task_description=task.description,
                    result={"output": result.output, "duration_seconds": result.duration_seconds, "errors": [result.error] if result.error else []} if result else None,
                    state=TaskState.COMPLETED if (result and result.success) else TaskState.FAILED,
                )
                evaluations.append(eval_result)

            for eval_result in evaluations:
                if eval_result.success:
                    self._learning.record_success(goal_description, plan.strategy.name if plan.strategy else "default", eval_result)
                else:
                    self._learning.record_failure(goal_description, plan.strategy.name if plan.strategy else "default", eval_result.error or "unknown")

            success = report.failed_tasks == 0
            return IntelligenceResult(
                goal=plan.goal,
                plan=plan,
                cognition=cognition,
                reasoning=reasoning,
                decisions=[decompose_decision],
                coordination=report,
                evaluations=evaluations,
                success=success,
            )

        except Exception as e:
            return IntelligenceResult(
                goal=Goal.create(description=goal_description, priority=priority),
                success=False,
                error=str(e),
            )

    def get_status(self) -> dict[str, Any]:
        plans = self._planner.list_plans()
        return {
            "active_goals": self._goal_manager.count(),
            "active_plans": len(plans),
            "policy": self._policy.get_current_policy().value,
            "total_learned": len(self._learning.get_all()),
            "metrics": {
                "total_executions": self._telemetry.get_metrics().total_executions,
                "successful": self._telemetry.get_metrics().successful_executions,
                "failed": self._telemetry.get_metrics().failed_executions,
                "avg_duration_seconds": self._telemetry.get_metrics().avg_duration_seconds,
            },
        }

    @property
    def goal_manager(self) -> GoalManager:
        return self._goal_manager

    @property
    def planner(self) -> IntelligencePlanner:
        return self._planner

    @property
    def coordinator(self) -> CoordinatorEngine:
        return self._coordinator

    @property
    def telemetry(self) -> TelemetryEngine:
        return self._telemetry

    @property
    def learning(self) -> LearningEngine:
        return self._learning

    @property
    def policy(self) -> PolicyEngine:
        return self._policy

    @property
    def safety(self) -> SafetyEngine:
        return self._safety

    @property
    def context_manager(self) -> ContextManager:
        return self._context_manager
