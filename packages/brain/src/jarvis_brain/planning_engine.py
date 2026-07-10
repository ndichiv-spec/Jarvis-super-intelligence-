from __future__ import annotations

from jarvis_brain.models import (
    Capability,
    ExecutionContext,
    ExecutionPlan,
    ExecutionStrategy,
    Intent,
    IntentKind,
    PlanTask,
)


class DefaultPlanningEngine:
    def build_plan(self, intent: Intent, context: ExecutionContext) -> ExecutionPlan:
        _ = context
        tasks: list[PlanTask] = [
            PlanTask(
                task_id="prepare_execution",
                description="Prepare validated execution scope.",
                capability=Capability.RESPOND,
                dependencies=(),
                parallelizable=False,
                estimated_cost=1,
            )
        ]

        parallel_roots: list[str] = []
        if Capability.MEMORY_ACCESS in intent.required_capabilities:
            task_id = "load_memory_references"
            tasks.append(
                PlanTask(
                    task_id=task_id,
                    description="Resolve relevant memory references.",
                    capability=Capability.MEMORY_ACCESS,
                    dependencies=("prepare_execution",),
                    parallelizable=True,
                    estimated_cost=2,
                )
            )
            parallel_roots.append(task_id)

        if (
            Capability.KNOWLEDGE_QUERY in intent.required_capabilities
            or intent.kind == IntentKind.RESEARCH
        ):
            task_id = "load_knowledge_references"
            tasks.append(
                PlanTask(
                    task_id=task_id,
                    description="Resolve knowledge graph/document references.",
                    capability=Capability.KNOWLEDGE_QUERY,
                    dependencies=("prepare_execution",),
                    parallelizable=True,
                    estimated_cost=3,
                )
            )
            parallel_roots.append(task_id)

        if Capability.TOOL_COORDINATION in intent.required_capabilities:
            tasks.append(
                PlanTask(
                    task_id="prepare_tool_contracts",
                    description="Validate tool contracts for execution.",
                    capability=Capability.TOOL_COORDINATION,
                    dependencies=("prepare_execution",),
                    parallelizable=False,
                    estimated_cost=2,
                )
            )

        if Capability.AGENT_COORDINATION in intent.required_capabilities:
            tasks.append(
                PlanTask(
                    task_id="prepare_agent_contracts",
                    description="Select and prepare specialist agent contracts.",
                    capability=Capability.AGENT_COORDINATION,
                    dependencies=("prepare_execution",),
                    parallelizable=False,
                    estimated_cost=2,
                )
            )

        if intent.kind == IntentKind.CLARIFICATION:
            tasks.append(
                PlanTask(
                    task_id="request_clarification",
                    description="Prepare clarification request contract.",
                    capability=Capability.CLARIFICATION,
                    dependencies=("prepare_execution",),
                    parallelizable=False,
                    estimated_cost=1,
                )
            )

        final_dependencies = tuple(task.task_id for task in tasks)
        tasks.append(
            PlanTask(
                task_id="compose_structured_response",
                description="Compose structured response payload.",
                capability=Capability.RESPOND,
                dependencies=final_dependencies,
                parallelizable=False,
                estimated_cost=1,
            )
        )

        strategy = self._select_strategy(tasks, parallel_roots)
        required_capabilities = tuple(dict.fromkeys(task.capability for task in tasks))
        return ExecutionPlan(
            tasks=tuple(tasks),
            strategy=strategy,
            required_capabilities=required_capabilities,
            estimated_cost=sum(task.estimated_cost for task in tasks),
        )

    def _select_strategy(
        self,
        tasks: list[PlanTask],
        parallel_roots: list[str],
    ) -> ExecutionStrategy:
        if not parallel_roots:
            return ExecutionStrategy.SEQUENTIAL
        if len(parallel_roots) >= 2 and len(tasks) <= 5:
            return ExecutionStrategy.PARALLEL
        return ExecutionStrategy.HYBRID
