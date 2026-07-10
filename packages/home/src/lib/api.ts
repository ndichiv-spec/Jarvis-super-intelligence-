import type {
  DashboardStats,
  Conversation,
  Message,
  Project,
  MemoryItem,
  KnowledgeDocument,
  Automation,
  Agent,
  ToolDefinition,
  ExtensionInfo,
  Notification,
  SearchResult,
  UserProfile,
  Plan,
  CommunicationConversation,
  CommunicationMessage,
  CommunicationNotification,
  CommunicationPresence,
  CommunicationMetrics,
} from "@/types";

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${GATEWAY_URL}/gateway${path}`, {
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
    stats: () => fetchApi<DashboardStats>("/dashboard/stats"),
  },

  conversations: {
    list: () => fetchApi<Conversation[]>("/conversations"),
    get: (id: string) => fetchApi<Conversation>(`/conversations/${id}`),
    messages: (id: string) => fetchApi<Message[]>(`/conversations/${id}/messages`),
  },

  projects: {
    list: () => fetchApi<Project[]>("/projects"),
    get: (id: string) => fetchApi<Project>(`/projects/${id}`),
  },

  memory: {
    list: () => fetchApi<MemoryItem[]>("/memory"),
    archive: (id: string) => fetchApi<void>(`/memory/${id}/archive`, { method: "POST" }),
    delete: (id: string) => fetchApi<void>(`/memory/${id}`, { method: "DELETE" }),
  },

  knowledge: {
    search: (q: string) => fetchApi<KnowledgeDocument[]>(`/knowledge?q=${encodeURIComponent(q)}`),
    get: (id: string) => fetchApi<KnowledgeDocument>(`/knowledge/${id}`),
  },

  automations: {
    list: () => fetchApi<Automation[]>("/automations"),
  },

  agents: {
    list: () => fetchApi<Agent[]>("/agents"),
    get: (id: string) => fetchApi<Agent>(`/agents/${id}`),
  },

  tools: {
    list: () => fetchApi<ToolDefinition[]>("/tools"),
  },

  extensions: {
    list: () => fetchApi<ExtensionInfo[]>("/extensions"),
  },

  notifications: {
    list: () => fetchApi<Notification[]>("/notifications"),
    markRead: (id: string) => fetchApi<void>(`/notifications/${id}/read`, { method: "POST" }),
    markAllRead: () => fetchApi<void>("/notifications/read-all", { method: "POST" }),
  },

  search: {
    query: (q: string) => fetchApi<SearchResult[]>(`/search?q=${encodeURIComponent(q)}`),
  },

  profile: {
    get: () => fetchApi<UserProfile>("/profile"),
    update: (data: Partial<UserProfile>) =>
      fetchApi<UserProfile>("/profile", {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
  },

  planning: {
    create: (objective: string, templates?: string[]) =>
      fetchApi<Plan>(`/planning/create`, {
        method: "POST",
        body: JSON.stringify({ objective, templates }),
      }),
    get: (id: string) => fetchApi<Plan>(`/planning/${id}`),
    getStatus: (id: string) => fetchApi<Plan>(`/planning/${id}/status`),
    getGraph: (id: string) => fetchApi<unknown>(`/planning/${id}/graph`),
    execute: (planId: string) =>
      fetchApi<Plan>(`/planning/execute`, {
        method: "POST",
        body: JSON.stringify({ plan_id: planId }),
      }),
    cancel: (planId: string) =>
      fetchApi<void>(`/planning/${planId}/cancel`, { method: "POST" }),
    list: () => fetchApi<Plan[]>("/planning"),
  },

  communication: {
    conversations: () => fetchApi<CommunicationConversation[]>("/communication/conversations"),
    messages: (conversationId?: string) =>
      fetchApi<CommunicationMessage[]>(`/communication/messages${conversationId ? `?conversation_id=${conversationId}` : ""}`),
    notifications: (userId: string, unreadOnly = false) =>
      fetchApi<CommunicationNotification[]>(`/communication/notifications?user_id=${userId}${unreadOnly ? "&unread_only=true" : ""}`),
    presence: () => fetchApi<CommunicationPresence[]>("/communication/presence"),
    metrics: () => fetchApi<CommunicationMetrics>("/communication/metrics"),
    unread: (userId: string) => fetchApi<{ messages: number; notifications: number; total: number }>(`/communication/unread/${userId}`),
    sendMessage: (sender: string, receiver: string, body: string, conversationId?: string) =>
      fetchApi<{ message_id: string }>("/communication/messages", {
        method: "POST",
        body: JSON.stringify({ sender, receiver, body, conversation_id: conversationId }),
      }),
    markMessageRead: (messageId: string, userId: string) =>
      fetchApi<void>(`/communication/messages/${messageId}/read`, {
        method: "POST",
        body: JSON.stringify({ user_id: userId }),
      }),
    markAllNotificationsRead: (userId: string) =>
      fetchApi<void>("/communication/notifications/read-all", {
        method: "POST",
        body: JSON.stringify({ user_id: userId }),
      }),
  },
};
