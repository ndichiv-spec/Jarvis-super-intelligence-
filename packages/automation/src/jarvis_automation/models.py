from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class WorkflowStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    RETRYING = "retrying"
    COMPENSATING = "compensating"
    ARCHIVED = "archived"


class StepStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    WAITING_APPROVAL = "waiting_approval"
    COMPENSATING = "compensating"
    BLOCKED = "blocked"


class WorkflowCategory(StrEnum):
    RESEARCH = "research"
    ENGINEERING = "engineering"
    KNOWLEDGE_PROCESSING = "knowledge_processing"
    DOCUMENT_ANALYSIS = "document_analysis"
    PROJECT_PLANNING = "project_planning"
    TESTING = "testing"
    NOTIFICATION = "notification"
    APPROVAL = "approval"
    CUSTOM = "custom"


class StepType(StrEnum):
    TASK = "task"
    SUB_WORKFLOW = "sub_workflow"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    APPROVAL = "approval"
    COMPENSATION = "compensation"
    DELAY = "delay"


class ExecutionMode(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class TriggerType(StrEnum):
    MANUAL = "manual"
    BRAIN_DECISION = "brain_decision"
    AGENT_REQUEST = "agent_request"
    SCHEDULED = "scheduled"
    EVENT = "event"
    EXTERNAL_SIGNAL = "external_signal"
    USER_ACTION = "user_action"


class ScheduleType(StrEnum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    CRON = "cron"
    CALENDAR = "calendar"
    DELAY = "delay"
    INTERVAL = "interval"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class CompensationStrategy(StrEnum):
    UNDO_PREVIOUS = "undo_previous"
    REVERSE_ACTION = "reverse_action"
    COMPENSATING_TRANSACTION = "compensating_transaction"
    PARTIAL_ROLLBACK = "partial_rollback"
    FAILURE_RECOVERY = "failure_recovery"


class RetryStrategy(StrEnum):
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ALTERNATIVE_PATH = "alternative_path"
    ESCALATION = "escalation"


class VariableScope(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    EXECUTION = "execution"
    CONTEXT = "context"
    SHARED = "shared"
    IMMUTABLE = "immutable"


# ---------------------------------------------------------------------------
# Core domain models
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class VariableDefinition:
    name: str
    type: str
    description: str
    scope: VariableScope = VariableScope.EXECUTION
    default: str | None = None
    required: bool = False


@dataclass(frozen=True, slots=True)
class WorkflowInput:
    name: str
    type: str
    description: str
    required: bool = True
    default: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowOutput:
    name: str
    type: str
    description: str


@dataclass(frozen=True, slots=True)
class WorkflowCondition:
    expression: str
    description: str
    then_step: str
    else_step: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowDependency:
    step_id: str
    depends_on: str
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    strategy: RetryStrategy = RetryStrategy.IMMEDIATE
    max_retries: int = 3
    delay_seconds: int = 0
    backoff_multiplier: float = 2.0
    max_delay_seconds: int = 3600
    alternative_step_id: str | None = None
    escalation_after: int = 0


@dataclass(frozen=True, slots=True)
class CompensationAction:
    action_id: str
    description: str
    strategy: CompensationStrategy = CompensationStrategy.UNDO_PREVIOUS
    step_id: str = ""
    requires_confirmation: bool = False


@dataclass(frozen=True, slots=True)
class ApprovalGate:
    gate_id: str
    description: str
    required_approvers: int = 1
    timeout_seconds: int = 86400
    allow_self_approval: bool = False


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    step_id: str
    name: str
    description: str
    step_type: StepType = StepType.TASK
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    tool_identifier: str = ""
    agent_identifier: str = ""
    sub_workflow_id: str = ""
    inputs: tuple[WorkflowInput, ...] = field(default_factory=tuple)
    outputs: tuple[WorkflowOutput, ...] = field(default_factory=tuple)
    variables: tuple[VariableDefinition, ...] = field(default_factory=tuple)
    conditions: tuple[WorkflowCondition, ...] = field(default_factory=tuple)
    dependencies: tuple[WorkflowDependency, ...] = field(default_factory=tuple)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    compensation: CompensationAction | None = None
    approval_gate: ApprovalGate | None = None
    timeout_seconds: int = 3600
    sub_steps: tuple[WorkflowStep, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    workflow_id: str
    name: str
    description: str
    version: str
    category: WorkflowCategory
    steps: tuple[WorkflowStep, ...]
    inputs: tuple[WorkflowInput, ...] = field(default_factory=tuple)
    outputs: tuple[WorkflowOutput, ...] = field(default_factory=tuple)
    variables: tuple[VariableDefinition, ...] = field(default_factory=tuple)
    owner: str = "system"
    workspace: str = "*"
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_updated_at(self) -> WorkflowDefinition:
        return replace(self, updated_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class WorkflowMetadata:
    workflow_id: str
    definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.CREATED
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_status(self, status: WorkflowStatus) -> WorkflowMetadata:
        return replace(self, status=status, updated_at=datetime.now(UTC))

    def with_definition(self, definition: WorkflowDefinition) -> WorkflowMetadata:
        return replace(self, definition=definition, updated_at=datetime.now(UTC))


# ---------------------------------------------------------------------------
# Execution models
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StepState:
    step_id: str
    status: StepStatus = StepStatus.PENDING
    attempts: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int = 0

    def with_status(self, status: StepStatus) -> StepState:
        return replace(self, status=status)

    def with_attempt(self) -> StepState:
        return replace(self, attempts=self.attempts + 1)

    def with_error(self, error: str) -> StepState:
        return replace(self, status=StepStatus.FAILED, error_message=error)


@dataclass(frozen=True, slots=True)
class WorkflowExecutionState:
    execution_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_step_id: str | None = None
    step_states: tuple[StepState, ...] = field(default_factory=tuple)
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def with_status(self, status: WorkflowStatus) -> WorkflowExecutionState:
        return replace(self, status=status)

    def with_current_step(self, step_id: str) -> WorkflowExecutionState:
        return replace(self, current_step_id=step_id)

    def with_step_state(self, step_state: StepState) -> WorkflowExecutionState:
        existing = {s.step_id: s for s in self.step_states}
        existing[step_state.step_id] = step_state
        return replace(self, step_states=tuple(existing.values()))


@dataclass(frozen=True, slots=True)
class ExecutionContextData:
    workflow_id: str
    execution_id: str
    correlation_id: str
    workspace: str = "*"
    project: str = "*"
    current_step_id: str = ""
    history: tuple[str, ...] = field(default_factory=tuple)

    def with_current_step(self, step_id: str) -> ExecutionContextData:
        return replace(
            self,
            current_step_id=step_id,
            history=(*self.history, step_id),
        )


@dataclass(frozen=True, slots=True)
class WorkflowExecutionRequest:
    execution_id: str
    workflow_id: str
    trigger_type: TriggerType
    correlation_id: str | None = None
    inputs: dict[str, str] = field(default_factory=dict)
    workspace: str = "*"
    project: str = "*"
    requested_by: str = "system"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class WorkflowExecutionResult:
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    outputs: dict[str, str] = field(default_factory=dict)
    error_message: str | None = None
    total_duration_ms: int = 0
    step_count: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Trigger & Schedule
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScheduleDefinition:
    schedule_id: str
    schedule_type: ScheduleType
    workflow_id: str
    cron_expression: str = ""
    interval_seconds: int = 0
    start_at: datetime | None = None
    end_at: datetime | None = None
    max_executions: int = 0
    parameters: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class TriggerDefinition:
    trigger_id: str
    trigger_type: TriggerType
    workflow_id: str
    name: str = ""
    description: str = ""
    event_pattern: str = ""
    schedule_id: str | None = None
    parameters: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class TriggerEvent:
    event_id: str
    trigger_type: TriggerType
    workflow_id: str
    payload: dict[str, str] = field(default_factory=dict)
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Approval
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    approval_id: str
    execution_id: str
    workflow_id: str
    step_id: str
    gate_id: str
    description: str
    requested_by: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: tuple[str, ...] = field(default_factory=tuple)
    expires_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_approval(self, approver: str) -> ApprovalRequest:
        return replace(
            self,
            status=ApprovalStatus.APPROVED,
            approved_by=(*self.approved_by, approver),
        )

    def with_rejection(self, approver: str) -> ApprovalRequest:
        return replace(
            self,
            status=ApprovalStatus.REJECTED,
            approved_by=(*self.approved_by, approver),
        )


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorkflowHealthReport:
    workflow_id: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration_ms: float = 0.0
    last_execution: datetime | None = None
    last_error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class MonitoringReport:
    report_id: str
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    step_duration_ms: dict[str, int] = field(default_factory=dict)
    total_duration_ms: int = 0
    retries: int = 0
    failures: int = 0
    resource_usage: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Policy
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AutomationPolicy:
    policy_id: str
    name: str
    max_concurrent_executions: int = 10
    max_executions_per_workflow: int = 100
    default_timeout_seconds: int = 3600
    workspace_restrictions: tuple[str, ...] = field(default_factory=lambda: ("*",))
    denied_workflows: tuple[str, ...] = field(default_factory=tuple)
    enterprise_governance: bool = False
    compliance_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class AutomationPolicyScope:
    owner: str = "*"
    workspace: str = "*"
    project: str = "*"
    is_enterprise: bool = False


# ---------------------------------------------------------------------------
# Variable manager
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class VariableValue:
    name: str
    value: str
    scope: VariableScope = VariableScope.EXECUTION
    immutable: bool = False
    description: str = ""


# ---------------------------------------------------------------------------
# Workflow templates
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorkflowTemplate:
    template_id: str
    name: str
    description: str
    category: WorkflowCategory
    definition: WorkflowDefinition
    tags: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
