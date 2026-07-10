from __future__ import annotations

from jarvis_brain.decision_engine import RuleBasedDecisionEngine
from jarvis_brain.models import (
    Capability,
    DecisionAction,
    ExecutionContext,
    ExecutionPlan,
    ExecutionStrategy,
    Intent,
    IntentKind,
    ReasoningMetadata,
    RiskLevel,
)


def test_decision_engine_requests_clarification_for_ambiguous_intent() -> None:
    decision = RuleBasedDecisionEngine().decide(
        intent=Intent(
            kind=IntentKind.RESEARCH,
            confidence=0.8,
            ambiguous=True,
            required_capabilities=(Capability.RESEARCH, Capability.CLARIFICATION),
            missing_information=("referent",),
            entities=(),
            normalized_query="research it",
        ),
        plan=ExecutionPlan(
            tasks=(),
            strategy=ExecutionStrategy.SEQUENTIAL,
            required_capabilities=(),
            estimated_cost=0,
        ),
        reasoning=ReasoningMetadata(
            selected_strategy=ExecutionStrategy.SEQUENTIAL,
            risk_level=RiskLevel.HIGH,
            risks=("ambiguous",),
            conflicts=(),
            priorities=(),
            rationale="",
        ),
        context=ExecutionContext({}, {}, (), (), {}, (), {}, {}, {}),
    )

    assert decision.action == DecisionAction.REQUEST_CLARIFICATION
    assert "referent" in decision.request_clarification_fields


def test_decision_engine_aborts_when_system_blocked() -> None:
    decision = RuleBasedDecisionEngine().decide(
        intent=Intent(
            kind=IntentKind.GENERAL_RESPONSE,
            confidence=0.9,
            ambiguous=False,
            required_capabilities=(Capability.RESPOND,),
            missing_information=(),
            entities=(),
            normalized_query="status",
        ),
        plan=ExecutionPlan(
            tasks=(),
            strategy=ExecutionStrategy.SEQUENTIAL,
            required_capabilities=(),
            estimated_cost=0,
        ),
        reasoning=ReasoningMetadata(
            selected_strategy=ExecutionStrategy.SEQUENTIAL,
            risk_level=RiskLevel.LOW,
            risks=(),
            conflicts=(),
            priorities=(),
            rationale="",
        ),
        context=ExecutionContext({}, {}, (), (), {}, (), {"execution_blocked": True}, {}, {}),
    )

    assert decision.action == DecisionAction.ABORT_EXECUTION
    assert decision.should_abort is True
