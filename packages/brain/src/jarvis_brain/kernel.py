from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from jarvis_brain.agent_coordinator import RuleBasedAgentCoordinator
from jarvis_brain.context_engine import MergeContextEngine
from jarvis_brain.decision_engine import RuleBasedDecisionEngine
from jarvis_brain.intent_engine import RuleBasedIntentEngine
from jarvis_brain.interfaces import (
    AgentCoordinator,
    ContextEngine,
    DecisionEngine,
    ExecutionTimeline,
    IntentEngine,
    MetricsCollector,
    PlanningEngine,
    ReasoningEngine,
    RequestProcessor,
    ResponseComposer,
    StructuredLogger,
    ToolCoordinator,
    Tracer,
    WorkflowEngine,
)
from jarvis_brain.models import (
    BrainExecutionState,
    BrainResponse,
    BrainStage,
    Capability,
    Decision,
    DecisionAction,
    ExecutionPlan,
    ExecutionStrategy,
    Intent,
    IntentKind,
    RawBrainRequest,
    ReasoningMetadata,
    RiskLevel,
)
from jarvis_brain.observability import (
    NullExecutionTimeline,
    NullMetricsCollector,
    NullStructuredLogger,
    NullTracer,
)
from jarvis_brain.planning_engine import DefaultPlanningEngine
from jarvis_brain.reasoning_engine import RuleBasedReasoningEngine
from jarvis_brain.request_processor import DefaultRequestProcessor
from jarvis_brain.response_composer import StructuredResponseComposer
from jarvis_brain.tool_coordinator import RuleBasedToolCoordinator
from jarvis_brain.workflow_engine import RuleBasedWorkflowEngine


@dataclass(frozen=True, slots=True)
class BrainKernelResult:
    response: BrainResponse
    state: BrainExecutionState


class BrainKernel:
    def __init__(
        self,
        *,
        request_processor: RequestProcessor | None = None,
        context_engine: ContextEngine | None = None,
        intent_engine: IntentEngine | None = None,
        planning_engine: PlanningEngine | None = None,
        reasoning_engine: ReasoningEngine | None = None,
        decision_engine: DecisionEngine | None = None,
        workflow_engine: WorkflowEngine | None = None,
        tool_coordinator: ToolCoordinator | None = None,
        agent_coordinator: AgentCoordinator | None = None,
        response_composer: ResponseComposer | None = None,
        logger: StructuredLogger | None = None,
        tracer: Tracer | None = None,
        metrics: MetricsCollector | None = None,
        timeline: ExecutionTimeline | None = None,
    ) -> None:
        self._request_processor = request_processor or DefaultRequestProcessor()
        self._context_engine = context_engine or MergeContextEngine()
        self._intent_engine = intent_engine or RuleBasedIntentEngine()
        self._planning_engine = planning_engine or DefaultPlanningEngine()
        self._reasoning_engine = reasoning_engine or RuleBasedReasoningEngine()
        self._decision_engine = decision_engine or RuleBasedDecisionEngine()
        self._workflow_engine = workflow_engine or RuleBasedWorkflowEngine()
        self._tool_coordinator = tool_coordinator or RuleBasedToolCoordinator()
        self._agent_coordinator = agent_coordinator or RuleBasedAgentCoordinator()
        self._response_composer = response_composer or StructuredResponseComposer()

        self._logger = logger or NullStructuredLogger()
        self._tracer = tracer or NullTracer()
        self._metrics = metrics or NullMetricsCollector()
        self._timeline = timeline or NullExecutionTimeline()

    def execute(self, raw_request: RawBrainRequest) -> BrainKernelResult:
        started = perf_counter()
        request = self._request_processor.process(raw_request)
        state = self._workflow_engine.initialize(request)
        self._timeline.record(state)

        self._tracer.start_span(
            request.trace_id,
            "brain.kernel.execute",
            {"execution_id": str(request.execution_id.value)},
        )
        self._logger.log("info", "brain.execution.initialized", {"trace_id": request.trace_id})

        fallback_context = request.context
        try:
            state = self._workflow_engine.start(state)
            self._timeline.record(state)

            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.REQUEST_PROCESSED,
                "Request processor normalized payload and initialized execution context.",
            )
            self._timeline.record(state)

            context = self._context_engine.build_context(request)
            fallback_context = context
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.CONTEXT_BUILT,
                "Context engine merged execution context.",
            )

            intent = self._intent_engine.determine_intent(request, context)
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.INTENT_DETERMINED,
                "Intent engine produced structured intent.",
            )

            plan = self._planning_engine.build_plan(intent, context)
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.PLAN_GENERATED,
                "Planning engine produced executable plan.",
            )

            reasoning = self._reasoning_engine.evaluate_plan(plan, intent, context)
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.PLAN_EVALUATED,
                "Reasoning engine evaluated risks and priorities.",
            )

            decision = self._decision_engine.decide(intent, plan, reasoning, context)
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.DECISION_MADE,
                "Decision engine selected final strategy.",
            )

            tools = self._tool_coordinator.prepare_tools(intent, plan, decision, context)
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.TOOLS_COORDINATED,
                "Tool coordinator prepared execution contracts.",
            )

            agents = self._agent_coordinator.prepare_agents(intent, plan, decision, context)
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.AGENTS_COORDINATED,
                "Agent coordinator prepared delegation contracts.",
            )

            response = self._response_composer.compose(
                state=state,
                intent=intent,
                plan=plan,
                reasoning=reasoning,
                decision=decision,
                tools=tools,
                agents=agents,
                context=context,
            )
            state = self._workflow_engine.complete_stage(
                state,
                BrainStage.RESPONSE_COMPOSED,
                "Response composer merged execution outputs.",
            )
            state = self._workflow_engine.complete(state)

            self._timeline.record(state)
            elapsed_ms = (perf_counter() - started) * 1000
            self._metrics.increment("brain.execution.completed")
            self._metrics.observe("brain.execution.latency_ms", elapsed_ms)
            self._logger.log(
                "info",
                "brain.execution.completed",
                {
                    "trace_id": request.trace_id,
                    "status": state.status.value,
                    "latency_ms": round(elapsed_ms, 2),
                },
            )
            return BrainKernelResult(response=response, state=state)

        except Exception as exc:
            failed_state = self._workflow_engine.fail(
                state,
                code="brain.pipeline.error",
                message=str(exc),
                stage=state.current_stage,
            )
            self._timeline.record(failed_state)
            self._metrics.increment("brain.execution.failed")
            self._logger.log(
                "error",
                "brain.execution.failed",
                {
                    "trace_id": request.trace_id,
                    "error": str(exc),
                    "stage": (
                        failed_state.current_stage.value
                        if failed_state.current_stage
                        else None
                    ),
                },
            )
            return BrainKernelResult(
                response=self._fallback_response(
                    state=failed_state,
                    raw_request=raw_request,
                    message=str(exc),
                    context=fallback_context,
                ),
                state=failed_state,
            )

    def _fallback_response(
        self,
        *,
        state: BrainExecutionState,
        raw_request: RawBrainRequest,
        message: str,
        context: object,
    ) -> BrainResponse:
        if not isinstance(context, type(raw_request.conversation_context)):
            context = raw_request
        fallback_intent = Intent(
            kind=IntentKind.CLARIFICATION,
            confidence=1.0,
            ambiguous=True,
            required_capabilities=(Capability.CLARIFICATION,),
            missing_information=("execution_failure",),
            entities=(),
            normalized_query=raw_request.message,
        )
        fallback_plan = ExecutionPlan(
            tasks=(),
            strategy=ExecutionStrategy.SEQUENTIAL,
            required_capabilities=(Capability.EXECUTION_ABORT,),
            estimated_cost=0,
        )
        fallback_reasoning = ReasoningMetadata(
            selected_strategy=ExecutionStrategy.SEQUENTIAL,
            risk_level=RiskLevel.CRITICAL,
            risks=(message,),
            conflicts=(),
            priorities=(),
            rationale="Execution aborted because the pipeline raised an exception.",
        )
        fallback_decision = Decision(
            action=DecisionAction.ABORT_EXECUTION,
            rationale="Pipeline failure",
            selected_strategy=ExecutionStrategy.SEQUENTIAL,
            request_clarification_fields=("execution_failure",),
            should_abort=True,
        )
        return BrainResponse(
            execution_id=state.execution_id,
            action=DecisionAction.ABORT_EXECUTION,
            intent=fallback_intent,
            plan=fallback_plan,
            reasoning=fallback_reasoning,
            decision=fallback_decision,
            tools=(),
            agents=(),
            references=raw_request.memory_references + raw_request.knowledge_references,
            execution_summary={
                "status": state.status.value,
                "error": message,
                "completed_stages": tuple(stage.value for stage in state.completed_stages),
            },
        )
