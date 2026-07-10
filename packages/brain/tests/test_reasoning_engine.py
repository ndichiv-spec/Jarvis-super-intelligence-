from __future__ import annotations

from jarvis_brain.models import (
    Capability,
    ExecutionContext,
    ExecutionPlan,
    ExecutionStrategy,
    Intent,
    IntentKind,
    PlanTask,
    RiskLevel,
)
from jarvis_brain.reasoning_engine import RuleBasedReasoningEngine


def test_reasoning_engine_detects_critical_risk_with_missing_information() -> None:
    intent = Intent(
        kind=IntentKind.RESEARCH,
        confidence=0.8,
        ambiguous=True,
        required_capabilities=(Capability.RESEARCH, Capability.RESPOND),
        missing_information=("referent",),
        entities=(),
        normalized_query="research it",
    )
    plan = ExecutionPlan(
        tasks=(
            PlanTask(
                task_id="prepare_execution",
                description="prepare",
                capability=Capability.RESPOND,
                dependencies=(),
                parallelizable=False,
                estimated_cost=1,
            ),
        ),
        strategy=ExecutionStrategy.SEQUENTIAL,
        required_capabilities=(Capability.RESPOND,),
        estimated_cost=1,
    )
    context = ExecutionContext({}, {}, (), (), {}, (), {}, {}, {})

    reasoning = RuleBasedReasoningEngine().evaluate_plan(plan, intent, context)

    assert reasoning.risk_level == RiskLevel.CRITICAL
    assert reasoning.conflicts


def test_reasoning_engine_low_risk_for_simple_plan() -> None:
    intent = Intent(
        kind=IntentKind.GENERAL_RESPONSE,
        confidence=0.9,
        ambiguous=False,
        required_capabilities=(Capability.RESPOND,),
        missing_information=(),
        entities=(),
        normalized_query="status",
    )
    plan = ExecutionPlan(
        tasks=(
            PlanTask(
                task_id="compose",
                description="compose",
                capability=Capability.RESPOND,
                dependencies=(),
                parallelizable=False,
                estimated_cost=1,
            ),
        ),
        strategy=ExecutionStrategy.SEQUENTIAL,
        required_capabilities=(Capability.RESPOND,),
        estimated_cost=1,
    )
    context = ExecutionContext({}, {}, (), (), {}, (), {}, {}, {})

    reasoning = RuleBasedReasoningEngine().evaluate_plan(plan, intent, context)

    assert reasoning.risk_level == RiskLevel.LOW
    assert not reasoning.risks
