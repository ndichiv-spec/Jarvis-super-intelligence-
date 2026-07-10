from __future__ import annotations

from types import MappingProxyType

from jarvis_brain.models import (
    AgentContract,
    BrainExecutionState,
    BrainResponse,
    Decision,
    ExecutionContext,
    ExecutionPlan,
    Intent,
    ReasoningMetadata,
    ToolContract,
)


class StructuredResponseComposer:
    def compose(
        self,
        state: BrainExecutionState,
        intent: Intent,
        plan: ExecutionPlan,
        reasoning: ReasoningMetadata,
        decision: Decision,
        tools: tuple[ToolContract, ...],
        agents: tuple[AgentContract, ...],
        context: ExecutionContext,
    ) -> BrainResponse:
        references = tuple(dict.fromkeys(context.memory_references + context.knowledge_references))
        summary = MappingProxyType(
            {
                "status": state.status.value,
                "stage": state.current_stage.value if state.current_stage else None,
                "completed_stages": tuple(stage.value for stage in state.completed_stages),
                "error_count": len(state.errors),
                "warning_count": len(state.warnings),
                "completed_tasks": state.metrics.completed_tasks,
                "failed_tasks": state.metrics.failed_tasks,
                "timeline_events": len(state.history),
            }
        )
        return BrainResponse(
            execution_id=state.execution_id,
            action=decision.action,
            intent=intent,
            plan=plan,
            reasoning=reasoning,
            decision=decision,
            tools=tools,
            agents=agents,
            references=references,
            execution_summary=summary,
        )
