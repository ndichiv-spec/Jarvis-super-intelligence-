import type {
  DashboardStats, Agent, WorkflowDefinition, WorkflowExecution,
  ToolDefinition, ToolExecution, ExtensionInfo,
  KnowledgeCollection, KnowledgeDocument, MemoryItem, MemoryPolicy,
  EventEntry, AIProvider, AIModel, SecurityUser, SecurityRole,
  SecurityPolicy, AuditLogEntry, InfrastructureComponent,
  MetricSeries, Alert, LogEntry, Trace, APIEndpoint,
  FeatureFlag, RuntimeConfig, Profile, DeveloperConsoleEntry,
  Workspace, Organization, Project, Plan,
} from "@/types";

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${GATEWAY_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.message || `API error: ${res.status}`);
  }
  const body = await res.json();
  if (!body.ok) throw new Error(body.error?.message || "API returned error");
  return body.data as T;
}

export const api = {
  dashboard: {
    stats: () => fetchApi<DashboardStats>("/studio/dashboard/stats"),
    metrics: () => fetchApi<MetricSeries[]>("/studio/dashboard/metrics"),
  },

  workspace: {
    list: () => fetchApi<Workspace[]>("/studio/workspaces"),
    get: (id: string) => fetchApi<Workspace>(`/studio/workspaces/${id}`),
    organizations: () => fetchApi<Organization[]>("/studio/organizations"),
    projects: (workspaceId: string) =>
      fetchApi<Project[]>(`/studio/workspaces/${workspaceId}/projects`),
  },

  agents: {
    list: () => fetchApi<Agent[]>("/studio/agents"),
    get: (id: string) => fetchApi<Agent>(`/studio/agents/${id}`),
    health: () => fetchApi<Record<string, unknown>>("/studio/agents/health"),
  },

  workflows: {
    list: () => fetchApi<WorkflowDefinition[]>("/studio/workflows"),
    get: (id: string) => fetchApi<WorkflowDefinition>(`/studio/workflows/${id}`),
    executions: (workflowId: string) =>
      fetchApi<WorkflowExecution[]>(`/studio/workflows/${workflowId}/executions`),
    execution: (id: string) => fetchApi<WorkflowExecution>(`/studio/workflows/executions/${id}`),
  },

  tools: {
    list: () => fetchApi<ToolDefinition[]>("/studio/tools"),
    get: (id: string) => fetchApi<ToolDefinition>(`/studio/tools/${id}`),
    executions: (toolId: string) =>
      fetchApi<ToolExecution[]>(`/studio/tools/${toolId}/executions`),
  },

  extensions: {
    list: () => fetchApi<ExtensionInfo[]>("/studio/extensions"),
    get: (id: string) => fetchApi<ExtensionInfo>(`/studio/extensions/${id}`),
    install: (id: string) => fetchApi<ExtensionInfo>(`/studio/extensions/${id}/install`, { method: "POST" }),
    uninstall: (id: string) => fetchApi<void>(`/studio/extensions/${id}`, { method: "DELETE" }),
    update: (id: string) => fetchApi<ExtensionInfo>(`/studio/extensions/${id}/update`, { method: "POST" }),
  },

  knowledge: {
    collections: () => fetchApi<KnowledgeCollection[]>("/studio/knowledge/collections"),
    collection: (id: string) => fetchApi<KnowledgeCollection>(`/studio/knowledge/collections/${id}`),
    documents: (collectionId: string) =>
      fetchApi<KnowledgeDocument[]>(`/studio/knowledge/collections/${collectionId}/documents`),
    search: (q: string) =>
      fetchApi<KnowledgeDocument[]>(`/studio/knowledge/search?q=${encodeURIComponent(q)}`),
  },

  memory: {
    list: () => fetchApi<MemoryItem[]>("/studio/memory"),
    policies: () => fetchApi<MemoryPolicy[]>("/studio/memory/policies"),
    archive: (id: string) => fetchApi<void>(`/studio/memory/${id}/archive`, { method: "POST" }),
    delete: (id: string) => fetchApi<void>(`/studio/memory/${id}`, { method: "DELETE" }),
  },

  events: {
    stream: () => fetchApi<EventEntry[]>("/studio/events/stream"),
    search: (params: Record<string, string>) => {
      const qs = new URLSearchParams(params).toString();
      return fetchApi<EventEntry[]>(`/studio/events?${qs}`);
    },
    get: (id: string) => fetchApi<EventEntry>(`/studio/events/${id}`),
  },

  ai: {
    providers: () => fetchApi<AIProvider[]>("/studio/ai/providers"),
    models: (providerId: string) =>
      fetchApi<AIModel[]>(`/studio/ai/providers/${providerId}/models`),
    usage: () => fetchApi<Record<string, unknown>>("/studio/ai/usage"),
  },

  security: {
    users: () => fetchApi<SecurityUser[]>("/studio/security/users"),
    roles: () => fetchApi<SecurityRole[]>("/studio/security/roles"),
    policies: () => fetchApi<SecurityPolicy[]>("/studio/security/policies"),
    auditLog: () => fetchApi<AuditLogEntry[]>("/studio/security/audit"),
  },

  infrastructure: {
    components: () => fetchApi<InfrastructureComponent[]>("/studio/infrastructure"),
    health: () => fetchApi<Record<string, unknown>>("/studio/infrastructure/health"),
  },

  observability: {
    metrics: () => fetchApi<MetricSeries[]>("/studio/observability/metrics"),
    logs: () => fetchApi<LogEntry[]>("/studio/observability/logs"),
    traces: () => fetchApi<Trace[]>("/studio/observability/traces"),
    alerts: () => fetchApi<Alert[]>("/studio/observability/alerts"),
  },

  apiExplorer: {
    endpoints: () => fetchApi<APIEndpoint[]>("/studio/api-explorer/endpoints"),
    execute: (method: string, path: string, body?: unknown) =>
      fetchApi<unknown>(`/studio/api-explorer/execute`, {
        method: "POST",
        body: JSON.stringify({ method, path, body }),
      }),
  },

  config: {
    featureFlags: () => fetchApi<FeatureFlag[]>("/studio/config/feature-flags"),
    runtimeConfig: () => fetchApi<RuntimeConfig[]>("/studio/config/runtime"),
    profiles: () => fetchApi<Profile[]>("/studio/config/profiles"),
  },

  console: {
    logs: () => fetchApi<DeveloperConsoleEntry[]>("/studio/console/logs"),
    execute: (command: string) =>
      fetchApi<DeveloperConsoleEntry>("/studio/console/execute", {
        method: "POST",
        body: JSON.stringify({ command }),
      }),
  },

  planning: {
    list: () => fetchApi<Plan[]>("/planning"),
    get: (id: string) => fetchApi<Plan>(`/planning/${id}`),
    create: (objective: string, templates?: string[]) =>
      fetchApi<Plan>(`/planning/create`, {
        method: "POST",
        body: JSON.stringify({ objective, templates }),
      }),
    getStatus: (id: string) => fetchApi<Plan>(`/planning/${id}/status`),
    getGraph: (id: string) => fetchApi<unknown>(`/planning/${id}/graph`),
    execute: (planId: string) =>
      fetchApi<Plan>(`/planning/execute`, {
        method: "POST",
        body: JSON.stringify({ plan_id: planId }),
      }),
    replan: (planId: string, reason: string, context?: Record<string, unknown>) =>
      fetchApi<unknown>(`/planning/replan`, {
        method: "POST",
        body: JSON.stringify({ plan_id: planId, reason, context }),
      }),
    cancel: (planId: string) =>
      fetchApi<void>(`/planning/${planId}/cancel`, { method: "POST" }),
  },
};
