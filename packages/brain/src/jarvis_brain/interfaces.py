from __future__ import annotations

from typing import Protocol

from jarvis_brain.models import (
    AgentContract,
    BrainExecutionState,
    BrainRequest,
    BrainResponse,
    BrainStage,
    Decision,
    ExecutionContext,
    ExecutionPlan,
    Intent,
    RawBrainRequest,
    ReasoningMetadata,
    ToolContract,
)


class StructuredLogger(Protocol):
    def log(self, level: str, event: str, data: dict[str, object]) -> None: ...


class Tracer(Protocol):
    def start_span(self, trace_id: str, name: str, attributes: dict[str, object]) -> None: ...


class MetricsCollector(Protocol):
    def increment(self, metric: str, value: int = 1) -> None: ...

    def observe(self, metric: str, value: float) -> None: ...


class ExecutionTimeline(Protocol):
    def record(self, state: BrainExecutionState) -> None: ...


class RequestProcessor(Protocol):
    def process(self, raw_request: RawBrainRequest) -> BrainRequest: ...


class ContextEngine(Protocol):
    def build_context(self, request: BrainRequest) -> ExecutionContext: ...


class IntentEngine(Protocol):
    def determine_intent(self, request: BrainRequest, context: ExecutionContext) -> Intent: ...


class PlanningEngine(Protocol):
    def build_plan(self, intent: Intent, context: ExecutionContext) -> ExecutionPlan: ...


class ReasoningEngine(Protocol):
    def evaluate_plan(
        self,
        plan: ExecutionPlan,
        intent: Intent,
        context: ExecutionContext,
    ) -> ReasoningMetadata: ...


class DecisionEngine(Protocol):
    def decide(
        self,
        intent: Intent,
        plan: ExecutionPlan,
        reasoning: ReasoningMetadata,
        context: ExecutionContext,
    ) -> Decision: ...


class WorkflowEngine(Protocol):
    def initialize(self, request: BrainRequest) -> BrainExecutionState: ...

    def start(self, state: BrainExecutionState) -> BrainExecutionState: ...

    def complete_stage(
        self,
        state: BrainExecutionState,
        stage: BrainStage,
        details: str,
    ) -> BrainExecutionState: ...

    def fail(
        self,
        state: BrainExecutionState,
        code: str,
        message: str,
        stage: BrainStage | None,
    ) -> BrainExecutionState: ...

    def complete(self, state: BrainExecutionState) -> BrainExecutionState: ...

    def pause(self, state: BrainExecutionState, details: str) -> BrainExecutionState: ...

    def cancel(self, state: BrainExecutionState, details: str) -> BrainExecutionState: ...

    def retry(self, state: BrainExecutionState, details: str) -> BrainExecutionState: ...

    def rollback(self, state: BrainExecutionState, details: str) -> BrainExecutionState: ...


class ToolCoordinator(Protocol):
    def prepare_tools(
        self,
        intent: Intent,
        plan: ExecutionPlan,
        decision: Decision,
        context: ExecutionContext,
    ) -> tuple[ToolContract, ...]: ...


class AgentCoordinator(Protocol):
    def prepare_agents(
        self,
        intent: Intent,
        plan: ExecutionPlan,
        decision: Decision,
        context: ExecutionContext,
    ) -> tuple[AgentContract, ...]: ...


class ResponseComposer(Protocol):
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
    ) -> BrainResponse: ...
