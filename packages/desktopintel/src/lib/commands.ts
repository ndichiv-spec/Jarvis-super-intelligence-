import type {
  DesktopState,
  PermissionGrant,
  PermissionRequest,
  SyncStatus,
  OfflineStatus,
  UpdateStatus,
  DiagnosticsReport,
  DesktopCommand,
  DesktopSettings,
  NotificationItem,
  FileOperation,
  IntegrationContract,
  AuditEvent,
  CachedConversation,
  CachedKnowledge,
  QueuedAction,
} from "@/types";

const isTauri = typeof window !== "undefined" && "__TAURI__" in window;

async function invoke<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (isTauri) {
    const { invoke: tauriInvoke } = await import("@tauri-apps/api/core");
    return tauriInvoke<T>(cmd, args);
  }
  return mockInvoke<T>(cmd, args);
}

function mockInvoke<T>(_cmd: string, _args?: Record<string, unknown>): T {
  return getMockData(_cmd) as T;
}

function getMockData(cmd: string): unknown {
  const mocks: Record<string, unknown> = {
    get_runtime_status: {
      version: "1.0.0",
      startedAt: new Date(Date.now() - 3600000).toISOString(),
      uptime: 3600,
      sessionId: crypto.randomUUID(),
      gatewayConnected: true,
      capabilities: ["permissions", "sync", "file", "notifications", "offline", "updates", "palette", "settings", "diagnostics", "audit", "integrations"],
    },
    get_permissions: {
      granted: [
        { id: crypto.randomUUID(), permission: "file:read", resource: "Selected Files", grantedAt: new Date().toISOString(), revoked: false },
        { id: crypto.randomUUID(), permission: "file:write", resource: "Selected Files", grantedAt: new Date().toISOString(), revoked: false },
        { id: crypto.randomUUID(), permission: "notification:send", resource: "System Notifications", grantedAt: new Date().toISOString(), revoked: false },
        { id: crypto.randomUUID(), permission: "clipboard:write", resource: "Clipboard", grantedAt: new Date().toISOString(), revoked: false },
        { id: crypto.randomUUID(), permission: "integration:launch", resource: "Local Applications", grantedAt: new Date().toISOString(), revoked: false },
        { id: crypto.randomUUID(), permission: "network:connect", resource: "Gateway Connection", grantedAt: new Date().toISOString(), revoked: false },
      ],
      pending: [
        { id: crypto.randomUUID(), permission: "clipboard:read", resource: "Clipboard", reason: "Paste content into conversation", source: "Workspace Chat", requestedAt: new Date().toISOString(), status: "pending" as const },
        { id: crypto.randomUUID(), permission: "screen:capture", resource: "Screen", reason: "Share screen in collaboration session", source: "Collaboration Panel", requestedAt: new Date().toISOString(), status: "pending" as const },
      ],
      history: [
        { id: crypto.randomUUID(), permission: "folder:select", action: "granted" as const, resource: "Downloads Folder", timestamp: new Date().toISOString(), actor: "User" },
        { id: crypto.randomUUID(), permission: "camera:access", action: "denied" as const, resource: "Camera", timestamp: new Date(Date.now() - 86400000).toISOString(), actor: "User" },
      ],
    },
    get_sync_status: {
      state: "synced",
      lastSyncAt: new Date().toISOString(),
      pendingChanges: 0,
      conflicts: 0,
      modules: [
        { name: "Projects", state: "synced", lastSyncAt: new Date().toISOString(), itemCount: 12 },
        { name: "Conversations", state: "synced", lastSyncAt: new Date().toISOString(), itemCount: 48 },
        { name: "Preferences", state: "synced", lastSyncAt: new Date().toISOString(), itemCount: 24 },
        { name: "Settings", state: "synced", lastSyncAt: new Date().toISOString(), itemCount: 36 },
      ],
    },
    get_offline_status: {
      enabled: false,
      connected: true,
      cachedConversations: 0,
      cachedKnowledge: 0,
      pendingActions: 0,
      storageUsed: 0,
      storageLimit: 1073741824,
    },
    get_update_status: {
      currentVersion: "1.0.0",
      updateAvailable: false,
      channel: "stable",
      lastCheckedAt: new Date().toISOString(),
    },
    get_diagnostics: {
      runtime: { status: "healthy", pid: 12345, memoryUsage: 128, cpuUsage: 2.5, uptime: 3600 },
      gateway: { status: "connected", latency: 12, lastConnected: new Date().toISOString(), retryCount: 0 },
      sync: { status: "healthy", queueDepth: 0, failedSyncs: 0, lastSuccess: new Date().toISOString() },
      resources: { memory: 128, memoryLimit: 2048, cpu: 2.5, storage: 256, storageLimit: 5120 },
      errors: [],
    },
    get_commands: [
      { id: "nav-dashboard", title: "Dashboard", description: "Open the main dashboard", category: "navigation", icon: "LayoutDashboard", shortcut: "Ctrl+Shift+D" },
      { id: "nav-settings", title: "Settings", description: "Open desktop settings", category: "navigation", icon: "Settings", shortcut: "Ctrl+," },
      { id: "nav-permissions", title: "Permission Center", description: "Manage permissions", category: "navigation", icon: "Shield", shortcut: "Ctrl+Shift+P" },
      { id: "nav-diagnostics", title: "Diagnostics", description: "View local diagnostics", category: "navigation", icon: "Activity", shortcut: "Ctrl+Shift+X" },
      { id: "nav-audit", title: "Audit Log", description: "View audit trail", category: "navigation", icon: "ScrollText", shortcut: "Ctrl+Shift+A" },
      { id: "sync-now", title: "Sync Now", description: "Force workspace synchronization", category: "workspace", icon: "RefreshCw" },
      { id: "toggle-offline", title: "Toggle Offline Mode", description: "Enable or disable offline mode", category: "workspace", icon: "WifiOff" },
      { id: "check-updates", title: "Check for Updates", description: "Check for available updates", category: "workspace", icon: "Download" },
      { id: "open-file", title: "Open File", description: "Open a file from the file system", category: "file", icon: "FileUp" },
      { id: "save-file", title: "Save File", description: "Save content to a file", category: "file", icon: "FileDown" },
      { id: "toggle-sidebar", title: "Toggle Sidebar", description: "Show or hide the sidebar", category: "view", icon: "PanelLeft" },
      { id: "toggle-dark-mode", title: "Toggle Dark Mode", description: "Switch between light and dark themes", category: "view", icon: "Moon" },
      { id: "about", title: "About JARVIS Desktop", description: "View application information", category: "help", icon: "Info" },
    ],
    get_settings: {
      appearance: { theme: "system", fontSize: "medium", sidebarVisible: true, reducedMotion: false, compactMode: false },
      shortcuts: [
        { id: "toggle-palette", key: "k", modifiers: ["ctrl"], command: "Toggle Command Palette", category: "General" },
        { id: "open-settings", key: ",", modifiers: ["ctrl"], command: "Open Settings", category: "Navigation" },
        { id: "toggle-sidebar", key: "b", modifiers: ["ctrl"], command: "Toggle Sidebar", category: "View" },
        { id: "toggle-dark-mode", key: "d", modifiers: ["ctrl", "shift"], command: "Toggle Dark Mode", category: "View" },
        { id: "sync-now", key: "s", modifiers: ["ctrl", "shift"], command: "Sync Now", category: "Workspace" },
      ],
      notifications: { enabled: true, workflowComplete: true, agentRequests: true, securityAlerts: true, automationUpdates: true, systemMessages: true, soundEnabled: false },
      workspace: { defaultWorkspace: "", autoSync: true, syncInterval: 300, confirmBeforeAction: true },
      offline: { enableOfflineMode: false, cacheConversations: true, cacheKnowledge: true, cacheLimit: 500, autoSyncOnReconnect: true },
      general: { language: "en", telemetryEnabled: false, autoUpdate: true, updateChannel: "stable", logLevel: "info" },
    },
    get_notifications: [
      { id: crypto.randomUUID(), type: "workflow", title: "Workflow Complete", message: "Data Processing Pipeline completed successfully", severity: "success", timestamp: new Date().toISOString(), read: false },
      { id: crypto.randomUUID(), type: "security", title: "Login Detected", message: "New login from Chrome on Windows", severity: "info", timestamp: new Date(Date.now() - 300000).toISOString(), read: false },
      { id: crypto.randomUUID(), type: "system", title: "Update Available", message: "Version 1.1.0 is ready to install", severity: "info", timestamp: new Date(Date.now() - 600000).toISOString(), read: true },
      { id: crypto.randomUUID(), type: "automation", title: "Schedule Triggered", message: "Nightly backup automation started", severity: "info", timestamp: new Date(Date.now() - 900000).toISOString(), read: true },
      { id: crypto.randomUUID(), type: "agent", title: "Agent Request", message: "Research Agent needs file access permission", severity: "warning", timestamp: new Date(Date.now() - 1800000).toISOString(), read: true },
    ],
    get_file_operations: [
      { id: crypto.randomUUID(), type: "open", path: "/Documents/report.pdf", status: "completed", timestamp: new Date(Date.now() - 120000).toISOString(), size: 245000, mimeType: "application/pdf" },
      { id: crypto.randomUUID(), type: "save", path: "/Documents/export.csv", status: "completed", timestamp: new Date(Date.now() - 600000).toISOString(), size: 12000, mimeType: "text/csv" },
      { id: crypto.randomUUID(), type: "import", path: "/Downloads/data.json", status: "approved", timestamp: new Date(Date.now() - 1800000).toISOString(), size: 89000, mimeType: "application/json" },
    ],
    get_integration_contracts: [
      { id: "browser-001", name: "Browser Integration", application: "Web Browsers", type: "browser", capabilities: ["Open URLs", "Extract page content", "Fill forms"], protocols: ["http", "https"], version: "1.0.0", available: true },
      { id: "office-001", name: "Office Integration", application: "Microsoft Office / LibreOffice", type: "office", capabilities: ["Open documents", "Read spreadsheets", "Export presentations"], protocols: ["file", "odf"], version: "1.0.0", available: false },
      { id: "ide-001", name: "IDE Integration", application: "VS Code / JetBrains", type: "ide", capabilities: ["Open files at line", "Search workspace", "Read diagnostics"], protocols: ["file", "vscode", "jetbrains"], version: "1.0.0", available: true },
      { id: "pdf-001", name: "PDF Viewer Integration", application: "PDF Viewers", type: "pdf-viewer", capabilities: ["Open PDF", "Extract text", "Navigate pages"], protocols: ["file"], version: "1.0.0", available: false },
      { id: "fm-001", name: "File Manager Integration", application: "File Managers", type: "file-manager", capabilities: ["Reveal in folder", "Select files", "Create folders"], protocols: ["file"], version: "1.0.0", available: true },
      { id: "term-001", name: "Terminal Integration", application: "Terminals", type: "terminal", capabilities: ["Execute commands", "Read output", "Monitor processes"], protocols: ["shell"], version: "1.0.0", available: false },
    ],
    get_audit_events: [
      { id: crypto.randomUUID(), action: "file.open", module: "FileInteraction", permission: "file:read", resource: "/Documents/report.pdf", result: "allowed", timestamp: new Date().toISOString(), details: "User opened file via file dialog" },
      { id: crypto.randomUUID(), action: "file.save", module: "FileInteraction", permission: "file:write", resource: "/Documents/export.csv", result: "allowed", timestamp: new Date(Date.now() - 600000).toISOString(), details: "User saved exported content" },
      { id: crypto.randomUUID(), action: "sync.start", module: "Sync", permission: "network:connect", resource: "Workspace Sync", result: "allowed", timestamp: new Date(Date.now() - 1200000).toISOString(), details: "Workspace synchronization started" },
      { id: crypto.randomUUID(), action: "clipboard.read", module: "Permissions", permission: "clipboard:read", resource: "Clipboard", result: "denied", timestamp: new Date(Date.now() - 1800000).toISOString(), details: "Clipboard read request denied by user" },
      { id: crypto.randomUUID(), action: "notification.send", module: "Notifications", permission: "notification:send", resource: "System Notifications", result: "allowed", timestamp: new Date(Date.now() - 3600000).toISOString(), details: "Workflow completion notification displayed" },
    ],
    get_cached_conversations: [
      { id: crypto.randomUUID(), title: "Project Planning", preview: "We need to discuss the architecture for the new module...", updatedAt: new Date().toISOString(), messageCount: 24 },
      { id: crypto.randomUUID(), title: "Code Review: PR #142", preview: "The changes look good but we should refactor the error handling...", updatedAt: new Date(Date.now() - 3600000).toISOString(), messageCount: 18 },
    ],
    get_cached_knowledge: [
      { id: crypto.randomUUID(), title: "Architecture Overview", summary: "System architecture documentation for JARVIS platform", collection: "Technical Docs", cachedAt: new Date().toISOString() },
      { id: crypto.randomUUID(), title: "API Reference", summary: "Complete Service Gateway API reference", collection: "Technical Docs", cachedAt: new Date().toISOString() },
    ],
    get_queued_actions: [
      { id: crypto.randomUUID(), type: "sync.projects", payload: '{"workspaceId":"ws-1"}', queuedAt: new Date().toISOString(), retryCount: 0, status: "queued" },
    ],
    request_permission: { id: crypto.randomUUID(), status: "pending" },
    grant_permission: { success: true },
    deny_permission: { success: true },
    revoke_permission: { success: true },
    trigger_sync: { success: true },
    toggle_offline: { enabled: true },
    check_updates: { updateAvailable: false },
    apply_settings: { success: true },
    get_desktop_state: null,
  };
  return mocks[cmd] ?? null;
}

export const commands = {
  getRuntimeStatus: () => invoke<DesktopState["runtime"]>("get_runtime_status"),
  getPermissions: () => invoke<{ granted: PermissionGrant[]; pending: PermissionRequest[]; history: PermissionEvent[] }>("get_permissions"),
  getSyncStatus: () => invoke<SyncStatus>("get_sync_status"),
  getOfflineStatus: () => invoke<OfflineStatus>("get_offline_status"),
  getUpdateStatus: () => invoke<UpdateStatus>("get_update_status"),
  getDiagnostics: () => invoke<DiagnosticsReport>("get_diagnostics"),
  getCommands: () => invoke<DesktopCommand[]>("get_commands"),
  getSettings: () => invoke<DesktopSettings>("get_settings"),
  getNotifications: () => invoke<NotificationItem[]>("get_notifications"),
  getFileOperations: () => invoke<FileOperation[]>("get_file_operations"),
  getIntegrationContracts: () => invoke<IntegrationContract[]>("get_integration_contracts"),
  getAuditEvents: () => invoke<AuditEvent[]>("get_audit_events"),
  getCachedConversations: () => invoke<CachedConversation[]>("get_cached_conversations"),
  getCachedKnowledge: () => invoke<CachedKnowledge[]>("get_cached_knowledge"),
  getQueuedActions: () => invoke<QueuedAction[]>("get_queued_actions"),
  requestPermission: (permission: string, resource: string, reason: string) =>
    invoke<{ id: string; status: string }>("request_permission", { permission, resource, reason }),
  grantPermission: (id: string) => invoke<{ success: boolean }>("grant_permission", { id }),
  denyPermission: (id: string) => invoke<{ success: boolean }>("deny_permission", { id }),
  revokePermission: (id: string) => invoke<{ success: boolean }>("revoke_permission", { id }),
  triggerSync: () => invoke<{ success: boolean }>("trigger_sync"),
  toggleOffline: (enabled: boolean) => invoke<{ enabled: boolean }>("toggle_offline", { enabled }),
  checkUpdates: () => invoke<{ updateAvailable: boolean }>("check_updates"),
  applySettings: (settings: Partial<DesktopSettings>) =>
    invoke<{ success: boolean }>("apply_settings", { settings }),
  markNotificationRead: (id: string) => invoke<{ success: boolean }>("mark_notification_read", { id }),
  clearNotifications: () => invoke<{ success: boolean }>("clear_notifications"),
  openFile: () => invoke<{ path: string }>("open_file"),
  saveFile: (content: string, defaultName: string) =>
    invoke<{ path: string }>("save_file", { content, defaultName }),
};
