import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Sidebar } from "@/components/layout/sidebar";
import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";

describe("Sidebar", () => {
  beforeEach(() => {
    useDesktopStore.setState({
      activePage: "dashboard",
      setActivePage: vi.fn(),
      state: {
        runtime: { version: "1.0.0", startedAt: "", uptime: 0, sessionId: "", gatewayConnected: true, capabilities: [] },
        permissions: { granted: [], pending: [], history: [] },
        sync: { state: "synced", lastSyncAt: "", pendingChanges: 0, conflicts: 0, modules: [] },
        offline: { enabled: false, connected: true, cachedConversations: 0, cachedKnowledge: 0, pendingActions: 0, storageUsed: 0, storageLimit: 1073741824 },
        updates: { currentVersion: "1.0.0", updateAvailable: false, channel: "stable", lastCheckedAt: "" },
        diagnostics: {
          runtime: { status: "healthy", pid: 0, memoryUsage: 0, cpuUsage: 0, uptime: 0 },
          gateway: { status: "connected", latency: 0, lastConnected: "", retryCount: 0 },
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
    } as any);
    useUIStore.setState({
      sidebarOpen: true,
      toggleSidebar: vi.fn(),
      notificationPanelOpen: false,
      commandPaletteOpen: false,
      settingsDialogOpen: false,
      permissionDialogOpen: false,
    });
  });

  it("renders all navigation items", () => {
    render(<Sidebar />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Permission Center")).toBeInTheDocument();
    expect(screen.getByText("Workspace Sync")).toBeInTheDocument();
    expect(screen.getByText("File Operations")).toBeInTheDocument();
    expect(screen.getByText("Integrations")).toBeInTheDocument();
    expect(screen.getByText("Notifications")).toBeInTheDocument();
    expect(screen.getByText("Offline Mode")).toBeInTheDocument();
    expect(screen.getByText("Updates")).toBeInTheDocument();
    expect(screen.getByText("Diagnostics")).toBeInTheDocument();
    expect(screen.getByText("Audit Log")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("active item has correct class", () => {
    render(<Sidebar />);
    const buttons = screen.getAllByRole("button");
    const dashboardBtn = buttons.find((b) => b.textContent?.includes("Dashboard"));
    expect(dashboardBtn).toHaveClass("bg-accent");
  });

  it("clicking an item calls setActivePage", () => {
    const setActivePage = vi.fn();
    useDesktopStore.setState({ setActivePage });
    render(<Sidebar />);
    fireEvent.click(screen.getByText("Permission Center"));
    expect(setActivePage).toHaveBeenCalledWith("permissions");
  });

  it("toggle sidebar button works", () => {
    const toggleSidebar = vi.fn();
    useUIStore.setState({ toggleSidebar });
    const { container } = render(<Sidebar />);
    const toggleBtn = container.querySelector("aside button");
    fireEvent.click(toggleBtn!);
    expect(toggleSidebar).toHaveBeenCalledOnce();
  });
});
