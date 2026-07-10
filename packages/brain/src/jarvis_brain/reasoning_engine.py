from __future__ import annotations

from jarvis_core import PriorityLevel

from jarvis_brain.models import (
    Capability,
    ExecutionContext,
    ExecutionPlan,
    ExecutionStrategy,
    Intent,
    ReasoningMetadata,
    RiskLevel,
    TaskPriority,
)


class RuleBasedReasoningEngine:
    def evaluate_plan(
        self,
        plan: ExecutionPlan,
        intent: Intent,
        context: ExecutionContext,
    ) -> ReasoningMetadata:
        _ = context
        risks: list[str] = []
        conflicts: list[str] = []

        if intent.ambiguous:
            risks.append("Intent is ambiguous and may require clarification.")
        if intent.missing_information:
            conflicts.append(
                f"Missing request data: {', '.join(intent.missing_information)}"
            )
        if plan.estimated_cost > 10:
            risks.append("Plan cost is high and may require staged execution.")
        if plan.strategy == ExecutionStrategy.PARALLEL and any(
            task.capability == Capability.TOOL_COORDINATION for task in plan.tasks
        ):
            risks.append("Parallel tool coordination increases operational risk.")

        risk_level = self._derive_risk_level(
            risks=tuple(risks),
            conflicts=tuple(conflicts),
        )
        priorities = tuple(
            self._priority_for_task(task.capability, task.task_id)
            for task in plan.tasks
        )
        rationale = self._build_rationale(
            risk_level=risk_level,
            risks=tuple(risks),
            conflicts=tuple(conflicts),
        )

        return ReasoningMetadata(
            selected_strategy=plan.strategy,
            risk_level=risk_level,
            risks=tuple(risks),
            conflicts=tuple(conflicts),
            priorities=priorities,
            rationale=rationale,
        )

    def _derive_risk_level(
        self,
        *,
        risks: tuple[str, ...],
        conflicts: tuple[str, ...],
    ) -> RiskLevel:
        if conflicts:
            return RiskLevel.CRITICAL
        if len(risks) >= 2:
            return RiskLevel.HIGH
        if len(risks) == 1:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _priority_for_task(self, capability: Capability, task_id: str) -> TaskPriority:
        match capability:
            case Capability.CLARIFICATION | Capability.EXECUTION_ABORT:
                return TaskPriority(
                    task_id=task_id,
                    priority=PriorityLevel.CRITICAL,
                    reason="Safety gate",
                )
            case Capability.TOOL_COORDINATION | Capability.AGENT_COORDINATION:
                return TaskPriority(
                    task_id=task_id,
                    priority=PriorityLevel.HIGH,
                    reason="External orchestration dependencies",
                )
            case Capability.RESEARCH:
                return TaskPriority(
                    task_id=task_id,
                    priority=PriorityLevel.HIGH,
                    reason="Research latency",
                )
            case _:
                return TaskPriority(
                    task_id=task_id,
                    priority=PriorityLevel.NORMAL,
                    reason="Standard flow",
                )

    def _build_rationale(
        self,
        *,
        risk_level: RiskLevel,
        risks: tuple[str, ...],
        conflicts: tuple[str, ...],
    ) -> str:
        if risk_level == RiskLevel.LOW:
            return "Plan is safe for direct execution."
        reasons = [*risks, *conflicts]
        return f"Plan requires guarded execution: {'; '.join(reasons)}"
