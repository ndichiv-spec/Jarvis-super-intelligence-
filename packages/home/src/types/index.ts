export type Theme = "light" | "dark" | "system";

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
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
  projectCount: number;
  activeAgentCount: number;
  lastActivity: Date;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: "active" | "completed" | "archived" | "paused";
  progress: number;
  milestoneCount: number;
  memoryCount: number;
  conversationCount: number;
  updatedAt: Date;
}

export interface Conversation {
  id: string;
  title: string;
  preview: string;
  agentId?: string;
  messageCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  conversationId: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  attachments?: Attachment[];
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export interface Attachment {
  id: string;
  type: "image" | "file" | "code" | "reference";
  name: string;
  size?: number;
  url?: string;
  mimeType?: string;
}

export interface MemoryItem {
  id: string;
  content: string;
  type: "fact" | "preference" | "context" | "relationship";
  source: string;
  confidence: number;
  createdAt: Date;
  updatedAt: Date;
  archived: boolean;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  summary: string;
  collection: string;
  type: "document" | "reference" | "source" | "note";
  tags: string[];
  updatedAt: Date;
}

export interface Automation {
  id: string;
  name: string;
  description: string;
  status: "running" | "scheduled" | "completed" | "failed" | "paused";
  type: "workflow" | "trigger" | "schedule";
  lastRun?: Date;
  nextRun?: Date;
  executionCount: number;
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
}

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  status: "available" | "busy" | "error" | "disabled";
  executionCount: number;
  lastUsed?: Date;
}

export interface ExtensionInfo {
  id: string;
  name: string;
  description: string;
  publisher: string;
  version: string;
  type: string;
  status: "installed" | "active" | "disabled" | "error" | "updatable";
  permissions: string[];
  hasUpdate: boolean;
}

export interface Notification {
  id: string;
  type: "workflow" | "agent" | "security" | "platform" | "user";
  title: string;
  message: string;
  severity: "info" | "success" | "warning" | "error";
  read: boolean;
  timestamp: Date;
  actionUrl?: string;
}

export interface DashboardStats {
  activeProjects: number;
  activeAgents: number;
  runningAutomations: number;
  recentConversations: number;
  memoryItems: number;
  knowledgeDocuments: number;
  unreadNotifications: number;
  platformHealth: "healthy" | "degraded" | "critical";
  uptime: number;
}

export interface SearchResult {
  id: string;
  type: "conversation" | "project" | "memory" | "knowledge" | "agent" | "tool" | "extension";
  title: string;
  description: string;
  url: string;
  score: number;
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

export interface CommunicationMessage {
  message_id: string;
  sender: string;
  receiver: string;
  channel: string;
  conversation_id: string | null;
  message_type: string;
  priority: string;
  body: string;
  subject: string | null;
  timestamp: string;
  delivery_status: string;
  read_status: string;
}

export interface CommunicationConversation {
  conversation_id: string;
  title: string;
  participants: string[];
  message_count: number;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

export interface CommunicationNotification {
  notification_id: string;
  title: string;
  body: string;
  level: string;
  source: string;
  read: boolean;
  timestamp: string;
}

export interface CommunicationPresence {
  user_id: string;
  status: string;
  current_activity: string;
  last_seen: string | null;
  connected_clients: number;
}

export interface CommunicationMetrics {
  messages_sent: number;
  notifications_sent: number;
  active_sessions: number;
  active_presence: number;
  conversation_count: number;
}
