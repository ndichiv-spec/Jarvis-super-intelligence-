from __future__ import annotations

from jarvis_brain.models import (
    Decision,
    DecisionAction,
    ExecutionContext,
    ExecutionPlan,
    Intent,
    IntentKind,
    ReasoningMetadata,
    RiskLevel,
)


class RuleBasedDecisionEngine:
    def decide(
        self,
        intent: Intent,
        plan: ExecutionPlan,
        reasoning: ReasoningMetadata,
        context: ExecutionContext,
    ) -> Decision:
        _ = plan
        if intent.ambiguous or intent.missing_information:
            fields = tuple(
                dict.fromkeys((*intent.missing_information, "intent_scope"))
            )
            return Decision(
                action=DecisionAction.REQUEST_CLARIFICATION,
                rationale="Request is ambiguous or incomplete.",
                selected_strategy=reasoning.selected_strategy,
                request_clarification_fields=fields,
                should_abort=False,
            )

        if context.system_state.get("execution_blocked") is True:
            return Decision(
                action=DecisionAction.ABORT_EXECUTION,
                rationale="System state disallows execution.",
                selected_strategy=reasoning.selected_strategy,
                request_clarification_fields=(),
                should_abort=True,
            )

        if reasoning.risk_level == RiskLevel.CRITICAL:
            return Decision(
                action=DecisionAction.ABORT_EXECUTION,
                rationale="Critical risks or conflicts were detected.",
                selected_strategy=reasoning.selected_strategy,
                request_clarification_fields=(),
                should_abort=True,
            )

        match intent.kind:
            case IntentKind.RESEARCH:
                action = DecisionAction.RESEARCH
            case IntentKind.MEMORY:
                action = DecisionAction.USE_MEMORY
            case IntentKind.KNOWLEDGE:
                action = DecisionAction.QUERY_KNOWLEDGE
            case IntentKind.TOOL_WORKFLOW:
                action = DecisionAction.INVOKE_TOOLS
            case IntentKind.AGENT_WORKFLOW:
                action = DecisionAction.DELEGATE_TO_AGENTS
            case IntentKind.CLARIFICATION:
                action = DecisionAction.REQUEST_CLARIFICATION
            case _:
                action = DecisionAction.RESPOND

        return Decision(
            action=action,
            rationale=f"Action selected from intent kind: {intent.kind.value}.",
            selected_strategy=reasoning.selected_strategy,
            request_clarification_fields=(),
            should_abort=False,
        )
