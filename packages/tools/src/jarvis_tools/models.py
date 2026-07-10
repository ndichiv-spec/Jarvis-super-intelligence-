from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum


class ToolStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    FAILED = "failed"
    UNDER_MAINTENANCE = "under_maintenance"


class ExecutionStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    RETRY_REQUESTED = "retry_requested"


class ToolCategory(StrEnum):
    DOCUMENT_PROCESSING = "document_processing"
    SEARCH = "search"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    CODE_EXECUTION = "code_execution"
    MATHEMATICS = "mathematics"
    TRANSLATION = "translation"
    FORMATTING = "formatting"
    NOTIFICATION = "notification"
    DATA_CONVERSION = "data_conversion"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    UTILITY = "utility"
    CUSTOM = "custom"


class ToolCapability(StrEnum):
    DOCUMENT_PROCESSING = "document_processing"
    SEARCH = "search"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    CODE_EXECUTION = "code_execution"
    MATHEMATICS = "mathematics"
    TRANSLATION = "translation"
    FORMATTING = "formatting"
    NOTIFICATION = "notification"
    DATA_CONVERSION = "data_conversion"
    KNOWLEDGE_QUERY = "knowledge_query"
    MEMORY_ACCESS = "memory_access"
    TEXT_SUMMARIZATION = "text_summarization"
    TEXT_ANALYSIS = "text_analysis"
    DATA_VALIDATION = "data_validation"
    CUSTOM = "custom"


class PermissionAccess(StrEnum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class PermissionResource(StrEnum):
    WORKSPACE = "workspace"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    TOOL = "tool"
    COMMUNICATION = "communication"
    EXTERNAL_SYSTEM = "external_system"


@dataclass(frozen=True, slots=True)
class ToolProperty:
    name: str
    type: str
    description: str
    required: bool = True
    default: str | None = None


@dataclass(frozen=True, slots=True)
class ToolSchema:
    properties: tuple[ToolProperty, ...] = field(default_factory=tuple)
    description: str = ""


@dataclass(frozen=True, slots=True)
class ToolPermission:
    resource: PermissionResource
    access: PermissionAccess
    scope: str = "*"
    description: str = ""


@dataclass(frozen=True, slots=True)
class ToolExecutionPolicy:
    timeout_seconds: int = 300
    max_retries: int = 3
    allowed_workspaces: tuple[str, ...] = field(default_factory=lambda: ("*",))
    requires_confirmation: bool = False
    resource_limits: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    identifier: str
    name: str
    description: str
    version: str
    category: ToolCategory
    capabilities: tuple[ToolCapability, ...]
    input_schema: ToolSchema
    output_schema: ToolSchema
    permissions: tuple[ToolPermission, ...]
    execution_policy: ToolExecutionPolicy = field(default_factory=ToolExecutionPolicy)
    metadata: dict[str, str] = field(default_factory=dict)
    status: ToolStatus = ToolStatus.ACTIVE
    owner: str = "system"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_status(self, status: ToolStatus) -> ToolDefinition:
        return replace(self, status=status, updated_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ToolMetadata:
    identifier: str
    definition: ToolDefinition
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def with_definition(self, definition: ToolDefinition) -> ToolMetadata:
        return replace(self, definition=definition, updated_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ToolExecutionRequest:
    request_id: str
    tool_identifier: str
    agent_id: str
    parameters: dict[str, str]
    workspace: str = "*"
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    request_id: str
    status: ExecutionStatus
    output: str
    error_message: str | None = None
    execution_time_ms: int = 0
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ToolValidationReport:
    tool_identifier: str
    valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ToolHealthReport:
    tool_identifier: str
    available: bool
    execution_count: int = 0
    failure_count: int = 0
    average_execution_time_ms: float = 0.0
    last_execution: datetime | None = None
    status: ToolStatus = ToolStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ToolPolicy:
    policy_id: str
    name: str
    max_executions_per_minute: int = 60
    max_concurrent_executions: int = 10
    default_timeout_seconds: int = 300
    workspace_restrictions: tuple[str, ...] = field(default_factory=lambda: ("*",))
    enterprise_governance: bool = False
    denied_tools: tuple[str, ...] = field(default_factory=tuple)
    compliance_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ToolPolicyScope:
    owner: str = "*"
    workspace: str = "*"
    project: str = "*"
    is_enterprise: bool = False
