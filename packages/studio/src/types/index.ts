export type Theme = "light" | "dark" | "system";

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
  organizationId?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: Theme;
  sidebarCollapsed: boolean;
  fontSize: "small" | "medium" | "large";
  reducedMotion: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  description: string;
  environment: "development" | "staging" | "production";
  organizationId: string;
  projectCount: number;
  activeAgentCount: number;
  lastActivity: Date;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description: string;
  memberCount: number;
  workspaceCount: number;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  workspaceId: string;
  status: "active" | "completed" | "archived" | "paused";
  progress: number;
  updatedAt: Date;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: "active" | "idle" | "busy" | "error" | "disabled";
  capabilities: string[];
  model: string;
  currentTask?: string;
  taskCount: number;
  uptime: number;
  version: string;
  config: Record<string, unknown>;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  version: string;
  status: "draft" | "published" | "archived";
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  variables: WorkflowVariable[];
  updatedAt: Date;
}

export interface WorkflowNode {
  id: string;
  type: "trigger" | "action" | "condition" | "approval" | "retry" | "parallel" | "subworkflow";
  label: string;
  config: Record<string, unknown>;
  position: { x: number; y: number };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  condition?: string;
}

export interface WorkflowVariable {
  name: string;
  type: "string" | "number" | "boolean" | "object" | "array";
  defaultValue?: unknown;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: "running" | "completed" | "failed" | "paused" | "pending";
  startedAt: Date;
  completedAt?: Date;
  duration: number;
  trigger: string;
  error?: string;
}

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  status: "available" | "busy" | "error" | "disabled";
  permissions: string[];
  executionCount: number;
  lastUsed?: Date;
  metadata: Record<string, unknown>;
}

export interface ToolExecution {
  id: string;
  toolId: string;
  status: "success" | "failure" | "running";
  duration: number;
  timestamp: Date;
  error?: string;
}

export interface ExtensionInfo {
  id: string;
  name: string;
  description: string;
  publisher: string;
  version: string;
  latestVersion?: string;
  type: string;
  status: "installed" | "active" | "disabled" | "error" | "updatable";
  permissions: string[];
  hasUpdate: boolean;
  installedAt: Date;
}

export interface KnowledgeCollection {
  id: string;
  name: string;
  description: string;
  documentCount: number;
  type: "vector" | "graph" | "hybrid";
  updatedAt: Date;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  summary: string;
  collectionId: string;
  type: "document" | "reference" | "source" | "note";
  tags: string[];
  relationships: KnowledgeRelationship[];
  updatedAt: Date;
}

export interface KnowledgeRelationship {
  id: string;
  sourceId: string;
  targetId: string;
  type: "related" | "derived" | "references" | "part-of";
  label: string;
}

export interface MemoryItem {
  id: string;
  content: string;
  type: "fact" | "preference" | "context" | "relationship";
  source: string;
  confidence: number;
  reasoning: string;
  createdAt: Date;
  updatedAt: Date;
  archived: boolean;
  ttl?: Date;
}

export interface MemoryPolicy {
  id: string;
  name: string;
  type: "retention" | "archival" | "deletion";
  criteria: Record<string, unknown>;
  enabled: boolean;
}

export interface EventEntry {
  id: string;
  type: string;
  source: string;
  correlationId: string;
  data: Record<string, unknown>;
  timestamp: Date;
  severity: "info" | "warning" | "error" | "debug";
}

export interface AIModel {
  id: string;
  name: string;
  providerId: string;
  capabilities: string[];
  status: "available" | "busy" | "error";
  usage: ModelUsage;
}

export interface AIProvider {
  id: string;
  name: string;
  type: string;
  status: "healthy" | "degraded" | "error";
  models: AIModel[];
  usage: ModelUsage;
  latency: number;
}

export interface ModelUsage {
  totalCalls: number;
  tokensIn: number;
  tokensOut: number;
  cost: number;
}

export interface SecurityUser {
  id: string;
  name: string;
  email: string;
  role: string;
  status: "active" | "inactive" | "suspended";
  lastActive: Date;
  mfaEnabled: boolean;
}

export interface SecurityRole {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  userCount: number;
}

export interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  rules: SecurityRule[];
  enabled: boolean;
}

export interface SecurityRule {
  id: string;
  resource: string;
  action: "allow" | "deny";
  principals: string[];
  conditions?: Record<string, unknown>;
}

export interface AuditLogEntry {
  id: string;
  actor: string;
  action: string;
  resource: string;
  details: string;
  ip: string;
  timestamp: Date;
}

export interface InfrastructureComponent {
  id: string;
  name: string;
  type: "database" | "cache" | "vector-store" | "message-broker" | "storage" | "adapter";
  status: "healthy" | "degraded" | "critical" | "maintenance";
  latency: number;
  uptime: number;
  lastChecked: Date;
}

export interface MetricSeries {
  label: string;
  value: number;
  timestamp: Date;
}

export interface Alert {
  id: string;
  title: string;
  severity: "critical" | "warning" | "info";
  source: string;
  message: string;
  timestamp: Date;
  acknowledged: boolean;
}

export interface LogEntry {
  id: string;
  level: "debug" | "info" | "warn" | "error";
  source: string;
  message: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export interface Trace {
  id: string;
  name: string;
  duration: number;
  status: "success" | "error";
  spans: Span[];
  timestamp: Date;
}

export interface Span {
  id: string;
  name: string;
  duration: number;
  status: "success" | "error";
  parentId?: string;
}

export interface APIEndpoint {
  path: string;
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  description: string;
  version: string;
  parameters: APIParameter[];
  examples: Record<string, unknown>;
}

export interface APIParameter {
  name: string;
  type: string;
  required: boolean;
  description: string;
  location: "path" | "query" | "header" | "body";
}

export interface FeatureFlag {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  environment: string;
  updatedAt: Date;
}

export interface RuntimeConfig {
  key: string;
  value: string;
  type: "string" | "number" | "boolean" | "json";
  description: string;
  updatedAt: Date;
}

export interface Profile {
  id: string;
  name: string;
  description: string;
  config: Record<string, unknown>;
  active: boolean;
}

export interface DeveloperConsoleEntry {
  id: string;
  type: "log" | "diagnostic" | "validation" | "task" | "event";
  level: "info" | "warn" | "error" | "debug";
  message: string;
  source: string;
  timestamp: Date;
  data?: Record<string, unknown>;
}

export interface PlanGoal {
  objective: string;
  category: string;
  complexity: string;
  estimated_duration: string;
  risk_level: string;
  confidence: number;
}

export interface PlanTask {
  id: string;
  title: string;
  description: string;
  task_type: string;
  dependencies: string[];
  priority: number;
  assigned_agent: string;
  estimated_effort_hours: number;
  status?: string;
  group: string;
}

export interface PlanProgress {
  completion_percentage: number;
  completed_tasks: number;
  total_tasks: number;
  running_tasks: number;
  failed_tasks: number;
  blocked_tasks: number;
  waiting_tasks: number;
  active_task: string;
  estimated_remaining_seconds: number;
}

export interface Plan {
  id: string;
  objective: string;
  status: string;
  goal: PlanGoal | null;
  tasks: PlanTask[];
  progress: PlanProgress | null;
  created_at: string;
  updated_at: string;
}

export type DashboardStats = {
  activeProjects: number;
  activeAgents: number;
  runningWorkflows: number;
  totalTools: number;
  activeExtensions: number;
  platformHealth: "healthy" | "degraded" | "critical";
  uptime: number;
  alerts: number;
};
