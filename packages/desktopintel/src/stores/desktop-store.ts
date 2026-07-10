"use client";

import { create } from "zustand";
import type {
  Theme, DesktopState, PermissionGrant, PermissionRequest,
  PermissionEvent, SyncStatus, OfflineStatus, UpdateStatus,
  DiagnosticsReport, DesktopCommand, DesktopSettings, NotificationItem,
  FileOperation, IntegrationContract, AuditEvent,
  CachedConversation, CachedKnowledge, QueuedAction,
} from "@/types";
import { commands } from "@/lib/commands";

interface DesktopStore {
  state: DesktopState;
  notifications: NotificationItem[];
  fileOperations: FileOperation[];
  integrationContracts: IntegrationContract[];
  auditEvents: AuditEvent[];
  cachedConversations: CachedConversation[];
  cachedKnowledge: CachedKnowledge[];
  queuedActions: QueuedAction[];
  commands: DesktopCommand[];
  settings: DesktopSettings | null;
  paletteOpen: boolean;
  activePage: string;

  initialize: () => Promise<void>;
  setTheme: (theme: Theme) => void;
  setActivePage: (page: string) => void;
  setPaletteOpen: (open: boolean) => void;

  // Permissions
  grantPermission: (id: string) => Promise<void>;
  denyPermission: (id: string) => Promise<void>;
  revokePermission: (id: string) => Promise<void>;

  // Sync
  triggerSync: () => Promise<void>;

  // Offline
  toggleOffline: (enabled: boolean) => Promise<void>;

  // Updates
  checkUpdates: () => Promise<void>;

  // Settings
  updateSettings: (settings: Partial<DesktopSettings>) => Promise<void>;

  // Notifications
  markNotificationRead: (id: string) => Promise<void>;
  clearNotifications: () => Promise<void>;

  // Refresh
  refreshAll: () => Promise<void>;
}

export const useDesktopStore = create<DesktopStore>((set, get) => ({
  state: {
    runtime: { version: "", startedAt: "", uptime: 0, sessionId: "", gatewayConnected: false, capabilities: [] },
    permissions: { granted: [], pending: [], history: [] },
    sync: { state: "offline", lastSyncAt: "", pendingChanges: 0, conflicts: 0, modules: [] },
    offline: { enabled: false, connected: false, cachedConversations: 0, cachedKnowledge: 0, pendingActions: 0, storageUsed: 0, storageLimit: 1073741824 },
    updates: { currentVersion: "", updateAvailable: false, channel: "stable", lastCheckedAt: "" },
    diagnostics: {
      runtime: { status: "healthy", pid: 0, memoryUsage: 0, cpuUsage: 0, uptime: 0 },
      gateway: { status: "disconnected", latency: 0, lastConnected: "", retryCount: 0 },
      sync: { status: "healthy", queueDepth: 0, failedSyncs: 0, lastSuccess: "" },
      resources: { memory: 0, memoryLimit: 0, cpu: 0, storage: 0, storageLimit: 0 },
      errors: [],
    },
  },
  notifications: [],
  fileOperations: [],
  integrationContracts: [],
  auditEvents: [],
  cachedConversations: [],
  cachedKnowledge: [],
  queuedActions: [],
  commands: [],
  settings: null,
  paletteOpen: false,
  activePage: "dashboard",

  initialize: async () => {
    const [runtime, permissions, sync, offline, updates, diagnostics, cmds, settings, notifications, fileOps, contracts, audit, conversations, knowledge, queued] =
      await Promise.all([
        commands.getRuntimeStatus(),
        commands.getPermissions(),
        commands.getSyncStatus(),
        commands.getOfflineStatus(),
        commands.getUpdateStatus(),
        commands.getDiagnostics(),
        commands.getCommands(),
        commands.getSettings(),
        commands.getNotifications(),
        commands.getFileOperations(),
        commands.getIntegrationContracts(),
        commands.getAuditEvents(),
        commands.getCachedConversations(),
        commands.getCachedKnowledge(),
        commands.getQueuedActions(),
      ]);

    set({
      state: { runtime, permissions, sync, offline, updates, diagnostics },
      commands: cmds,
      settings,
      notifications,
      fileOperations: fileOps,
      integrationContracts: contracts,
      auditEvents: audit,
      cachedConversations: conversations,
      cachedKnowledge: knowledge,
      queuedActions: queued,
    });
  },

  setTheme: (theme) => {
    set((s) => s.settings ? { settings: { ...s.settings, appearance: { ...s.settings.appearance, theme } } } : {});
    const root = document.documentElement;
    if (theme === "dark") { root.classList.add("dark"); } else if (theme === "light") { root.classList.remove("dark"); }
    else {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.classList.toggle("dark", prefersDark);
    }
  },

  setActivePage: (page) => set({ activePage: page, paletteOpen: false }),
  setPaletteOpen: (open) => set({ paletteOpen: open }),

  grantPermission: async (id) => {
    await commands.grantPermission(id);
    const perms = await commands.getPermissions();
    set((s) => ({ state: { ...s.state, permissions: perms } }));
  },

  denyPermission: async (id) => {
    await commands.denyPermission(id);
    const perms = await commands.getPermissions();
    set((s) => ({ state: { ...s.state, permissions: perms } }));
  },

  revokePermission: async (id) => {
    await commands.revokePermission(id);
    const perms = await commands.getPermissions();
    set((s) => ({ state: { ...s.state, permissions: perms } }));
  },

  triggerSync: async () => {
    await commands.triggerSync();
    const sync = await commands.getSyncStatus();
    set((s) => ({ state: { ...s.state, sync } }));
  },

  toggleOffline: async (enabled) => {
    await commands.toggleOffline(enabled);
    const offline = await commands.getOfflineStatus();
    set((s) => ({ state: { ...s.state, offline } }));
  },

  checkUpdates: async () => {
    await commands.checkUpdates();
    const updates = await commands.getUpdateStatus();
    set((s) => ({ state: { ...s.state, updates } }));
  },

  updateSettings: async (partial) => {
    await commands.applySettings(partial);
    const settings = await commands.getSettings();
    set({ settings });
    if (partial.appearance?.theme) {
      get().setTheme(partial.appearance.theme);
    }
  },

  markNotificationRead: async (id) => {
    await commands.markNotificationRead(id);
    set((s) => ({ notifications: s.notifications.map((n) => n.id === id ? { ...n, read: true } : n) }));
  },

  clearNotifications: async () => {
    await commands.clearNotifications();
    set({ notifications: [] });
  },

  refreshAll: async () => {
    const { initialize } = get();
    await initialize();
  },
}));
