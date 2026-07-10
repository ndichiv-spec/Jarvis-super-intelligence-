export type Theme = "light" | "dark" | "system";

export interface DesktopState {
  runtime: RuntimeStatus;
  permissions: PermissionState;
  sync: SyncStatus;
  offline: OfflineStatus;
  updates: UpdateStatus;
  diagnostics: DiagnosticsReport;
}

export interface RuntimeStatus {
  version: string;
  startedAt: string;
  uptime: number;
  sessionId: string;
  gatewayConnected: boolean;
  capabilities: string[];
}

export interface PermissionState {
  granted: PermissionGrant[];
  pending: PermissionRequest[];
  history: PermissionEvent[];
}

export interface PermissionGrant {
  id: string;
  permission: PermissionType;
  resource: string;
  grantedAt: string;
  expiresAt?: string;
  revoked: boolean;
}

export type PermissionType =
  | "file:read"
  | "file:write"
  | "folder:select"
  | "clipboard:read"
  | "clipboard:write"
  | "notification:send"
  | "camera:access"
  | "microphone:access"
  | "screen:capture"
  | "integration:launch"
  | "network:connect"
  | "device:info";

export interface PermissionRequest {
  id: string;
  permission: PermissionType;
  resource: string;
  reason: string;
  source: string;
  requestedAt: string;
  status: "pending" | "approved" | "denied";
}

export interface PermissionEvent {
  id: string;
  permission: PermissionType;
  action: "granted" | "revoked" | "denied" | "expired";
  resource: string;
  timestamp: string;
  actor: string;
}

export interface SyncStatus {
  state: "synced" | "syncing" | "pending" | "error" | "offline";
  lastSyncAt: string;
  pendingChanges: number;
  conflicts: number;
  modules: SyncModule[];
}

export interface SyncModule {
  name: string;
  state: "synced" | "syncing" | "pending" | "error";
  lastSyncAt: string;
  itemCount: number;
}

export interface OfflineStatus {
  enabled: boolean;
  connected: boolean;
  cachedConversations: number;
  cachedKnowledge: number;
  pendingActions: number;
  storageUsed: number;
  storageLimit: number;
}

export interface UpdateStatus {
  currentVersion: string;
  availableVersion?: string;
  updateAvailable: boolean;
  channel: ReleaseChannel;
  lastCheckedAt: string;
}

export type ReleaseChannel = "stable" | "beta" | "nightly";

export interface DiagnosticsReport {
  runtime: RuntimeHealth;
  gateway: GatewayHealth;
  sync: SyncHealth;
  resources: ResourceUsage;
  errors: DiagnosticsError[];
}

export interface RuntimeHealth {
  status: "healthy" | "degraded" | "error";
  pid: number;
  memoryUsage: number;
  cpuUsage: number;
  uptime: number;
}

export interface GatewayHealth {
  status: "connected" | "disconnected" | "reconnecting";
  latency: number;
  lastConnected: string;
  retryCount: number;
}

export interface SyncHealth {
  status: "healthy" | "degraded" | "error";
  queueDepth: number;
  failedSyncs: number;
  lastSuccess: string;
}

export interface ResourceUsage {
  memory: number;
  memoryLimit: number;
  cpu: number;
  storage: number;
  storageLimit: number;
}

export interface DiagnosticsError {
  id: string;
  module: string;
  message: string;
  severity: "error" | "warning";
  timestamp: string;
  resolved: boolean;
}

export interface DesktopCommand {
  id: string;
  title: string;
  description: string;
  category: CommandCategory;
  shortcut?: string;
  icon: string;
}

export type CommandCategory =
  | "navigation"
  | "workspace"
  | "file"
  | "view"
  | "tools"
  | "help";

export interface DesktopShortcut {
  id: string;
  key: string;
  modifiers: string[];
  command: string;
  category: string;
}

export interface DesktopSettings {
  appearance: AppearanceSettings;
  shortcuts: DesktopShortcut[];
  notifications: NotificationSettings;
  workspace: WorkspaceSettings;
  offline: OfflineSettings;
  general: GeneralSettings;
}

export interface AppearanceSettings {
  theme: Theme;
  fontSize: "small" | "medium" | "large";
  sidebarVisible: boolean;
  reducedMotion: boolean;
  compactMode: boolean;
}

export interface NotificationSettings {
  enabled: boolean;
  workflowComplete: boolean;
  agentRequests: boolean;
  securityAlerts: boolean;
  automationUpdates: boolean;
  systemMessages: boolean;
  soundEnabled: boolean;
}

export interface WorkspaceSettings {
  defaultWorkspace: string;
  autoSync: boolean;
  syncInterval: number;
  confirmBeforeAction: boolean;
}

export interface OfflineSettings {
  enableOfflineMode: boolean;
  cacheConversations: boolean;
  cacheKnowledge: boolean;
  cacheLimit: number;
  autoSyncOnReconnect: boolean;
}

export interface GeneralSettings {
  language: string;
  telemetryEnabled: boolean;
  autoUpdate: boolean;
  updateChannel: ReleaseChannel;
  logLevel: "debug" | "info" | "warn" | "error";
}

export interface NotificationItem {
  id: string;
  type: "workflow" | "agent" | "security" | "automation" | "system";
  title: string;
  message: string;
  severity: "info" | "warning" | "error" | "success";
  timestamp: string;
  read: boolean;
  action?: string;
}

export interface FileOperation {
  id: string;
  type: "open" | "save" | "import" | "export";
  path: string;
  status: "pending" | "approved" | "completed" | "denied" | "error";
  timestamp: string;
  size: number;
  mimeType: string;
}

export interface IntegrationContract {
  id: string;
  name: string;
  application: string;
  type: IntegrationType;
  capabilities: string[];
  protocols: string[];
  version: string;
  available: boolean;
}

export type IntegrationType =
  | "browser"
  | "office"
  | "ide"
  | "pdf-viewer"
  | "file-manager"
  | "terminal";

export interface AuditEvent {
  id: string;
  action: string;
  module: string;
  permission: string;
  resource: string;
  result: "allowed" | "denied" | "error";
  timestamp: string;
  details: string;
}

export interface CachedConversation {
  id: string;
  title: string;
  preview: string;
  updatedAt: string;
  messageCount: number;
}

export interface CachedKnowledge {
  id: string;
  title: string;
  summary: string;
  collection: string;
  cachedAt: string;
}

export interface QueuedAction {
  id: string;
  type: string;
  payload: string;
  queuedAt: string;
  retryCount: number;
  status: "queued" | "processing" | "completed" | "failed";
}
