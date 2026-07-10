from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from jarvis_core import DomainIdentifier, PriorityLevel, Timestamp

ContextData = Mapping[str, object]


class Capability(StrEnum):
    RESPOND = "respond"
    RESEARCH = "research"
    MEMORY_ACCESS = "memory_access"
    KNOWLEDGE_QUERY = "knowledge_query"
    TOOL_COORDINATION = "tool_coordination"
    AGENT_COORDINATION = "agent_coordination"
    CLARIFICATION = "clarification"
    EXECUTION_ABORT = "execution_abort"


class IntentKind(StrEnum):
    GENERAL_RESPONSE = "general_response"
    RESEARCH = "research"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    TOOL_WORKFLOW = "tool_workflow"
    AGENT_WORKFLOW = "agent_workflow"
    CLARIFICATION = "clarification"


class ExecutionStrategy(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


class DecisionAction(StrEnum):
    RESPOND = "respond"
    RESEARCH = "research"
    USE_MEMORY = "use_memory"
    QUERY_KNOWLEDGE = "query_knowledge"
    INVOKE_TOOLS = "invoke_tools"
    DELEGATE_TO_AGENTS = "delegate_to_agents"
    REQUEST_CLARIFICATION = "request_clarification"
    ABORT_EXECUTION = "abort_execution"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    ROLLBACK = "rollback"


class BrainStage(StrEnum):
    REQUEST_PROCESSED = "request_processed"
    CONTEXT_BUILT = "context_built"
    INTENT_DETERMINED = "intent_determined"
    PLAN_GENERATED = "plan_generated"
    PLAN_EVALUATED = "plan_evaluated"
    DECISION_MADE = "decision_made"
    TOOLS_COORDINATED = "tools_coordinated"
    AGENTS_COORDINATED = "agents_coordinated"
    RESPONSE_COMPOSED = "response_composed"


@dataclass(frozen=True, slots=True)
class RawBrainRequest:
    message: str
    conversation_context: ContextData
    user_context: ContextData
    memory_references: tuple[str, ...]
    knowledge_references: tuple[str, ...]
    workspace_context: ContextData
    active_projects: tuple[str, ...]
    system_state: ContextData
    device_state: ContextData
    metadata: ContextData

    @classmethod
    def create(
        cls,
        message: str,
        *,
        conversation_context: Mapping[str, object] | None = None,
        user_context: Mapping[str, object] | None = None,
        memory_references: tuple[str, ...] = (),
        knowledge_references: tuple[str, ...] = (),
        workspace_context: Mapping[str, object] | None = None,
        active_projects: tuple[str, ...] = (),
        system_state: Mapping[str, object] | None = None,
        device_state: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> RawBrainRequest:
        return cls(
            message=message,
            conversation_context=MappingProxyType(dict(conversation_context or {})),
            user_context=MappingProxyType(dict(user_context or {})),
            memory_references=memory_references,
            knowledge_references=knowledge_references,
            workspace_context=MappingProxyType(dict(workspace_context or {})),
            active_projects=active_projects,
            system_state=MappingProxyType(dict(system_state or {})),
            device_state=MappingProxyType(dict(device_state or {})),
            metadata=MappingProxyType(dict(metadata or {})),
        )


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    conversation_context: ContextData
    user_context: ContextData
    memory_references: tuple[str, ...]
    knowledge_references: tuple[str, ...]
    workspace_context: ContextData
    active_projects: tuple[str, ...]
    system_state: ContextData
    device_state: ContextData
    merged_context: ContextData


@dataclass(frozen=True, slots=True)
class BrainRequest:
    execution_id: DomainIdentifier
    trace_id: str
    received_at: Timestamp
    normalized_message: str
    context: ExecutionContext
    metadata: ContextData


@dataclass(frozen=True, slots=True)
class Intent:
    kind: IntentKind
    confidence: float
    ambiguous: bool
    required_capabilities: tuple[Capability, ...]
    missing_information: tuple[str, ...]
    entities: tuple[str, ...]
    normalized_query: str


@dataclass(frozen=True, slots=True)
class PlanTask:
    task_id: str
    description: str
    capability: Capability
    dependencies: tuple[str, ...]
    parallelizable: bool
    estimated_cost: int


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    tasks: tuple[PlanTask, ...]
    strategy: ExecutionStrategy
    required_capabilities: tuple[Capability, ...]
    estimated_cost: int


@dataclass(frozen=True, slots=True)
class TaskPriority:
    task_id: str
    priority: PriorityLevel
    reason: str


@dataclass(frozen=True, slots=True)
class ReasoningMetadata:
    selected_strategy: ExecutionStrategy
    risk_level: RiskLevel
    risks: tuple[str, ...]
    conflicts: tuple[str, ...]
    priorities: tuple[TaskPriority, ...]
    rationale: str


@dataclass(frozen=True, slots=True)
class Decision:
    action: DecisionAction
    rationale: str
    selected_strategy: ExecutionStrategy
    request_clarification_fields: tuple[str, ...]
    should_abort: bool


@dataclass(frozen=True, slots=True)
class ToolContract:
    tool_name: str
    purpose: str
    required_permissions: tuple[str, ...]
    available: bool
    allowed: bool


@dataclass(frozen=True, slots=True)
class AgentContract:
    agent_name: str
    responsibility: str
    available: bool


@dataclass(frozen=True, slots=True)
class BrainIssue:
    code: str
    message: str
    stage: BrainStage | None


@dataclass(frozen=True, slots=True)
class ExecutionMetrics:
    completed_tasks: int
    failed_tasks: int
    warning_count: int


@dataclass(frozen=True, slots=True)
class ExecutionTimelineEntry:
    timestamp: Timestamp
    status: WorkflowStatus
    stage: BrainStage | None
    details: str


@dataclass(frozen=True, slots=True)
class BrainExecutionState:
    execution_id: DomainIdentifier
    trace_id: str
    created_at: Timestamp
    updated_at: Timestamp
    status: WorkflowStatus
    current_stage: BrainStage | None
    completed_stages: tuple[BrainStage, ...]
    errors: tuple[BrainIssue, ...]
    warnings: tuple[BrainIssue, ...]
    metrics: ExecutionMetrics
    history: tuple[ExecutionTimelineEntry, ...]


@dataclass(frozen=True, slots=True)
class BrainResponse:
    execution_id: DomainIdentifier
    action: DecisionAction
    intent: Intent
    plan: ExecutionPlan
    reasoning: ReasoningMetadata
    decision: Decision
    tools: tuple[ToolContract, ...]
    agents: tuple[AgentContract, ...]
    references: tuple[str, ...]
    execution_summary: Mapping[str, object]
