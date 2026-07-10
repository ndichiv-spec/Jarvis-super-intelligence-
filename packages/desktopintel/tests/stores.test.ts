import { describe, it, expect, beforeEach, vi } from "vitest";
import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";

const initialDesktopState = {
  state: {
    runtime: { version: "", startedAt: "", uptime: 0, sessionId: "", gatewayConnected: false, capabilities: [] },
    permissions: { granted: [], pending: [], history: [] },
    sync: { state: "offline" as const, lastSyncAt: "", pendingChanges: 0, conflicts: 0, modules: [] },
    offline: { enabled: false, connected: false, cachedConversations: 0, cachedKnowledge: 0, pendingActions: 0, storageUsed: 0, storageLimit: 1073741824 },
    updates: { currentVersion: "", updateAvailable: false, channel: "stable" as const, lastCheckedAt: "" },
    diagnostics: {
      runtime: { status: "healthy" as const, pid: 0, memoryUsage: 0, cpuUsage: 0, uptime: 0 },
      gateway: { status: "disconnected" as const, latency: 0, lastConnected: "", retryCount: 0 },
      sync: { status: "healthy" as const, queueDepth: 0, failedSyncs: 0, lastSuccess: "" },
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
};

describe("desktop-store", () => {
  beforeEach(() => {
    useDesktopStore.setState(initialDesktopState);
  });

  it("initializes with correct default state", () => {
    const s = useDesktopStore.getState();
    expect(s.state.runtime.version).toBe("");
    expect(s.activePage).toBe("dashboard");
    expect(s.paletteOpen).toBe(false);
    expect(s.settings).toBeNull();
    expect(s.commands).toEqual([]);
  });

  it("setActivePage updates activePage", () => {
    useDesktopStore.getState().setActivePage("settings");
    expect(useDesktopStore.getState().activePage).toBe("settings");
    expect(useDesktopStore.getState().paletteOpen).toBe(false);
  });

  it("setActivePage closes palette when open", () => {
    useDesktopStore.setState({ paletteOpen: true });
    useDesktopStore.getState().setActivePage("permissions");
    expect(useDesktopStore.getState().paletteOpen).toBe(false);
  });

  it("setPaletteOpen toggles palette", () => {
    useDesktopStore.getState().setPaletteOpen(true);
    expect(useDesktopStore.getState().paletteOpen).toBe(true);
    useDesktopStore.getState().setPaletteOpen(false);
    expect(useDesktopStore.getState().paletteOpen).toBe(false);
  });

  describe("setTheme", () => {
    it("adds dark class when theme is dark", () => {
      document.documentElement.classList.remove("dark");
      useDesktopStore.getState().setTheme("dark");
      expect(document.documentElement.classList.contains("dark")).toBe(true);
    });

    it("removes dark class when theme is light", () => {
      document.documentElement.classList.add("dark");
      useDesktopStore.getState().setTheme("light");
      expect(document.documentElement.classList.contains("dark")).toBe(false);
    });

    it("respects prefers-color-scheme when theme is system", () => {
      document.documentElement.classList.remove("dark");
      const original = window.matchMedia;
      window.matchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: true,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as unknown as typeof window.matchMedia;
      useDesktopStore.getState().setTheme("system");
      expect(document.documentElement.classList.contains("dark")).toBe(true);
      window.matchMedia = original;
    });
  });
});

describe("ui-store", () => {
  beforeEach(() => {
    useUIStore.setState({
      sidebarOpen: true,
      notificationPanelOpen: false,
      commandPaletteOpen: false,
      settingsDialogOpen: false,
      permissionDialogOpen: false,
    });
  });

  it("initializes with correct default state", () => {
    const s = useUIStore.getState();
    expect(s.sidebarOpen).toBe(true);
    expect(s.notificationPanelOpen).toBe(false);
    expect(s.commandPaletteOpen).toBe(false);
    expect(s.settingsDialogOpen).toBe(false);
    expect(s.permissionDialogOpen).toBe(false);
  });

  it("toggleSidebar toggles sidebarOpen", () => {
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(false);
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(true);
  });

  it("closeAllModals sets all modals to false", () => {
    useUIStore.setState({
      notificationPanelOpen: true,
      commandPaletteOpen: true,
      settingsDialogOpen: true,
      permissionDialogOpen: true,
    });
    useUIStore.getState().closeAllModals();
    const s = useUIStore.getState();
    expect(s.notificationPanelOpen).toBe(false);
    expect(s.commandPaletteOpen).toBe(false);
    expect(s.settingsDialogOpen).toBe(false);
    expect(s.permissionDialogOpen).toBe(false);
  });

  it("setSidebarOpen works", () => {
    useUIStore.getState().setSidebarOpen(false);
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it("setNotificationPanelOpen works", () => {
    useUIStore.getState().setNotificationPanelOpen(true);
    expect(useUIStore.getState().notificationPanelOpen).toBe(true);
  });

  it("setCommandPaletteOpen works", () => {
    useUIStore.getState().setCommandPaletteOpen(true);
    expect(useUIStore.getState().commandPaletteOpen).toBe(true);
  });

  it("setSettingsDialogOpen works", () => {
    useUIStore.getState().setSettingsDialogOpen(true);
    expect(useUIStore.getState().settingsDialogOpen).toBe(true);
  });

  it("setPermissionDialogOpen works", () => {
    useUIStore.getState().setPermissionDialogOpen(true);
    expect(useUIStore.getState().permissionDialogOpen).toBe(true);
  });
});
