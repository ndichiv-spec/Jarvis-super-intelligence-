from __future__ import annotations

from jarvis_brain.models import Capability, ExecutionContext, Intent, IntentKind
from jarvis_brain.planning_engine import DefaultPlanningEngine


def test_planning_engine_builds_parallel_research_plan() -> None:
    intent = Intent(
        kind=IntentKind.RESEARCH,
        confidence=0.9,
        ambiguous=False,
        required_capabilities=(
            Capability.RESEARCH,
            Capability.KNOWLEDGE_QUERY,
            Capability.MEMORY_ACCESS,
            Capability.RESPOND,
        ),
        missing_information=(),
        entities=("deployment",),
        normalized_query="research deployment",
    )
    context = ExecutionContext(
        conversation_context={},
        user_context={},
        memory_references=("mem-1",),
        knowledge_references=("kb-1",),
        workspace_context={},
        active_projects=("jarvis",),
        system_state={},
        device_state={},
        merged_context={},
    )

    plan = DefaultPlanningEngine().build_plan(intent, context)

    task_ids = {task.task_id for task in plan.tasks}
    assert "load_memory_references" in task_ids
    assert "load_knowledge_references" in task_ids
    assert "compose_structured_response" in task_ids
    assert plan.estimated_cost > 0
    assert len(plan.required_capabilities) >= 3
