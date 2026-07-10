from __future__ import annotations

import pytest
from jarvis_brain.models import BrainStage, RawBrainRequest, WorkflowStatus
from jarvis_brain.request_processor import DefaultRequestProcessor
from jarvis_brain.workflow_engine import RuleBasedWorkflowEngine, WorkflowTransitionError


def test_workflow_engine_happy_path_transitions() -> None:
    request = DefaultRequestProcessor().process(RawBrainRequest.create("status"))
    engine = RuleBasedWorkflowEngine()

    state = engine.initialize(request)
    state = engine.start(state)
    state = engine.complete_stage(state, BrainStage.REQUEST_PROCESSED, "done")
    state = engine.complete(state)

    assert state.status == WorkflowStatus.COMPLETED
    assert BrainStage.REQUEST_PROCESSED in state.completed_stages
    assert state.metrics.completed_tasks == 1


def test_workflow_engine_rejects_invalid_transition() -> None:
    request = DefaultRequestProcessor().process(RawBrainRequest.create("status"))
    engine = RuleBasedWorkflowEngine()
    state = engine.initialize(request)

    with pytest.raises(WorkflowTransitionError):
        engine.complete(state)
