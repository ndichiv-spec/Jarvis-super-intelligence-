from __future__ import annotations

from jarvis_brain.kernel import BrainKernel
from jarvis_brain.models import (
    BrainStage,
    DecisionAction,
    ExecutionContext,
    RawBrainRequest,
    WorkflowStatus,
)


def test_brain_kernel_executes_full_lifecycle(raw_request: RawBrainRequest) -> None:
    result = BrainKernel().execute(raw_request)

    assert result.state.status == WorkflowStatus.COMPLETED
    assert BrainStage.RESPONSE_COMPOSED in result.state.completed_stages
    assert result.response.execution_id == result.state.execution_id
    assert result.response.action in {
        DecisionAction.RESPOND,
        DecisionAction.RESEARCH,
        DecisionAction.INVOKE_TOOLS,
        DecisionAction.DELEGATE_TO_AGENTS,
        DecisionAction.USE_MEMORY,
        DecisionAction.QUERY_KNOWLEDGE,
        DecisionAction.REQUEST_CLARIFICATION,
    }


class FailingContextEngine:
    def build_context(self, request: object) -> ExecutionContext:
        _ = request
        raise RuntimeError("context merge failure")


def test_brain_kernel_handles_pipeline_failures(raw_request: RawBrainRequest) -> None:
    kernel = BrainKernel(context_engine=FailingContextEngine())

    result = kernel.execute(raw_request)

    assert result.state.status == WorkflowStatus.FAILED
    assert result.response.action == DecisionAction.ABORT_EXECUTION
    assert result.state.errors
