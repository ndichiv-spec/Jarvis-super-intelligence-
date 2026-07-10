from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserProfile:
    id: str
    name: str
    email: str
    role: str
    avatar: str | None = None
    organization_id: str | None = None


@dataclass
class WorkspaceInfo:
    id: str
    name: str
    description: str
    environment: str
    organization_id: str
    project_count: int = 0
    active_agent_count: int = 0
    last_activity: str = ""


@dataclass
class Organization:
    id: str
    name: str
    slug: str
    description: str
    member_count: int = 0
    workspace_count: int = 0


@dataclass
class DashboardStats:
    active_projects: int = 0
    active_agents: int = 0
    running_workflows: int = 0
    total_tools: int = 0
    active_extensions: int = 0
    platform_health: str = "healthy"
    uptime: float = 0
    alerts: int = 0


@dataclass
class MetricSeries:
    label: str = ""
    value: float = 0
    timestamp: str = ""


@dataclass
class ShellConfig:
    user: UserProfile | None = None
    current_workspace: WorkspaceInfo | None = None
    workspaces: list[WorkspaceInfo] = field(default_factory=list)
    organizations: list[Organization] = field(default_factory=list)
    notifications: list[dict] = field(default_factory=list)
    recent_items: list[dict] = field(default_factory=list)


@dataclass
class AgentInfo:
    id: str
    name: str
    description: str
    status: str = "idle"
    capabilities: list[str] = field(default_factory=list)
    model: str = ""
    task_count: int = 0
    uptime: float = 0
    version: str = "1.0.0"


@dataclass
class WorkflowDefinition:
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    status: str = "draft"
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    updated_at: str = ""


@dataclass
class WorkflowExecution:
    id: str
    workflow_id: str
    status: str = "pending"
    started_at: str = ""
    completed_at: str | None = None
    duration: float = 0
    trigger: str = ""
    error: str | None = None


@dataclass
class ToolDefinition:
    id: str
    name: str
    description: str
    category: str = ""
    status: str = "available"
    permissions: list[str] = field(default_factory=list)
    execution_count: int = 0


@dataclass
class ToolExecution:
    id: str
    tool_id: str
    status: str = "success"
    duration: float = 0
    timestamp: str = ""
    error: str | None = None


@dataclass
class ExtensionInfo:
    id: str
    name: str
    description: str
    publisher: str = ""
    version: str = "1.0.0"
    type: str = ""
    status: str = "active"
    permissions: list[str] = field(default_factory=list)
    has_update: bool = False


@dataclass
class KnowledgeCollection:
    id: str
    name: str
    description: str
    document_count: int = 0
    type: str = "vector"
    updated_at: str = ""


@dataclass
class KnowledgeDocument:
    id: str
    title: str
    summary: str
    collection_id: str
    type: str = "document"
    tags: list[str] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)


@dataclass
class MemoryItem:
    id: str
    content: str
    type: str = "fact"
    source: str = ""
    confidence: float = 1.0
    reasoning: str = ""
    created_at: str = ""
    updated_at: str = ""
    archived: bool = False


@dataclass
class MemoryPolicy:
    id: str
    name: str
    type: str = "retention"
    criteria: dict = field(default_factory=dict)
    enabled: bool = True


@dataclass
class EventEntry:
    id: str
    type: str
    source: str
    correlation_id: str = ""
    timestamp: str = ""
    severity: str = "info"


@dataclass
class AIProvider:
    id: str
    name: str
    type: str = ""
    status: str = "healthy"
    latency: float = 0


@dataclass
class AIModel:
    id: str
    name: str
    provider_id: str
    capabilities: list[str] = field(default_factory=list)
    status: str = "available"


@dataclass
class SecurityUser:
    id: str
    name: str
    email: str
    role: str = ""
    status: str = "active"
    mfa_enabled: bool = False


@dataclass
class SecurityRole:
    id: str
    name: str
    description: str
    permissions: list[str] = field(default_factory=list)
    user_count: int = 0


@dataclass
class SecurityPolicy:
    id: str
    name: str
    description: str
    rules: list[dict] = field(default_factory=list)
    enabled: bool = True


@dataclass
class AuditLogEntry:
    id: str
    actor: str
    action: str
    resource: str
    details: str = ""
    ip: str = ""
    timestamp: str = ""


@dataclass
class InfrastructureComponent:
    id: str
    name: str
    type: str = "database"
    status: str = "healthy"
    latency: float = 0
    uptime: float = 0


@dataclass
class LogEntry:
    id: str
    level: str = "info"
    source: str = ""
    message: str = ""
    timestamp: str = ""


@dataclass
class Trace:
    id: str
    name: str
    duration: float = 0
    status: str = "success"
    timestamp: str = ""
    spans: list[dict] = field(default_factory=list)


@dataclass
class Alert:
    id: str
    title: str
    severity: str = "info"
    source: str = ""
    message: str = ""
    timestamp: str = ""
    acknowledged: bool = False


@dataclass
class APIEndpoint:
    path: str
    method: str = "GET"
    description: str = ""
    version: str = "1.0"
    parameters: list[dict] = field(default_factory=list)


@dataclass
class FeatureFlag:
    key: str
    name: str
    description: str
    enabled: bool = False
    environment: str = ""
    updated_at: str = ""


@dataclass
class RuntimeConfig:
    key: str
    value: str = ""
    type: str = "string"
    description: str = ""
    updated_at: str = ""


@dataclass
class Profile:
    id: str
    name: str
    description: str
    config: dict = field(default_factory=dict)
    active: bool = False


@dataclass
class ConsoleEntry:
    id: str
    type: str = "log"
    level: str = "info"
    message: str = ""
    source: str = ""
    timestamp: str = ""


@dataclass
class CommunicationConversationEntry:
    id: str
    title: str
    participants: list[str]
    message_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    is_archived: bool = False


@dataclass
class CommunicationMessageEntry:
    id: str
    sender: str
    receiver: str
    channel: str = "internal"
    conversation_id: str | None = None
    body: str = ""
    message_type: str = "text"
    priority: str = "normal"
    timestamp: str = ""
    delivery_status: str = "pending"
    read_status: str = "unread"


@dataclass
class CommunicationStreamEntry:
    id: str
    stream_type: str = "ai_response"
    status: str = "active"
    started_at: str = ""
    chunk_count: int = 0


@dataclass
class CommunicationAnalyticsEntry:
    messages_sent: int = 0
    notifications_sent: int = 0
    active_conversations: int = 0
    active_users: int = 0
    active_streams: int = 0
    avg_response_time_ms: float = 0.0
    delivery_success_rate: float = 100.0
