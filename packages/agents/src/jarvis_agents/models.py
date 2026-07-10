from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum


class AgentStatus(StrEnum):
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    PAUSED = "paused"
    WAITING = "waiting"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    FAILED = "failed"
    RECOVERING = "recovering"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskStatus(StrEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentPermissionResource(StrEnum):
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    PROJECT = "project"
    WORKSPACE = "workspace"
    COMMUNICATION = "communication"
    EXTERNAL_SYSTEM = "external_system"


class PermissionAccess(StrEnum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True)
class AgentPermission:
    resource: AgentPermissionResource
    access: PermissionAccess
    scope: str = "*"


@dataclass(frozen=True, slots=True)
class AgentCapability:
    name: str
    description: str
    permission_required: AgentPermission | None = None


@dataclass(frozen=True, slots=True)
class AgentGoal:
    goal_id: str
    description: str
    priority: TaskPriority
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_progress(self, progress: float) -> AgentGoal:
        return replace(self, progress=progress, updated_at=datetime.now(UTC))

    def with_status(self, status: GoalStatus) -> AgentGoal:
        return replace(self, status=status, updated_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentTaskResult:
    success: bool
    output: str
    error_message: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentTask:
    task_id: str
    description: str
    assigned_agent_id: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    result: AgentTaskResult | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_status(self, status: TaskStatus) -> AgentTask:
        return replace(self, status=status, updated_at=datetime.now(UTC))

    def with_result(self, result: AgentTaskResult) -> AgentTask:
        return replace(self, result=result, updated_at=datetime.now(UTC))

    def increment_retry(self) -> AgentTask:
        return replace(self, retry_count=self.retry_count + 1, updated_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentCommunicationRequest:
    source_agent_id: str
    target_agent_id: str
    message_type: str
    payload: str
    correlation_id: str
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentCommunicationResponse:
    correlation_id: str
    source_agent_id: str
    target_agent_id: str
    payload: str
    success: bool
    error_message: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentEvent:
    event_id: str
    source_agent_id: str
    event_type: str
    payload: str
    broadcast: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentHealthReport:
    agent_id: str
    status: AgentStatus
    available: bool
    heartbeat_timestamp: datetime
    failure_count: int = 0
    last_failure_message: str | None = None
    performance_metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_heartbeat(self) -> AgentHealthReport:
        return replace(self, heartbeat_timestamp=datetime.now(UTC), created_at=datetime.now(UTC))

    def with_status(self, status: AgentStatus) -> AgentHealthReport:
        return replace(self, status=status, created_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentPolicy:
    policy_id: str
    name: str
    workspace_isolation: bool = True
    enterprise_governance: bool = False
    max_concurrent_tasks: int = 5
    max_retries_per_task: int = 3
    rate_limit_per_minute: int = 60
    execution_timeout_seconds: int = 3600
    allowed_capabilities: tuple[str, ...] = field(default_factory=lambda: ("*",))
    denied_capabilities: tuple[str, ...] = field(default_factory=tuple)
    compliance_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class AgentPolicyScope:
    owner: str = "*"
    workspace: str = "*"
    project: str = "*"
    is_enterprise: bool = False


@dataclass(frozen=True, slots=True)
class AgentMetadata:
    identifier: str
    name: str
    description: str
    role: str
    capabilities: tuple[AgentCapability, ...]
    permissions: tuple[AgentPermission, ...]
    version: str
    status: AgentStatus
    owner: str
    workspace: str
    policy_references: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_status(self, status: AgentStatus) -> AgentMetadata:
        return replace(self, status=status, updated_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    role: str
    description: str
    capabilities: tuple[AgentCapability, ...]
    permissions: tuple[AgentPermission, ...]
    default_policy_id: str = "agent-default"
    version: str = "1.0.0"
