import { describe, it, expect, beforeEach } from "vitest";
import { useAppStore } from "@/stores/app-store";
import type { Theme } from "@/types";

function createFreshStore() {
  const store = useAppStore;
  store.setState({
    theme: "system",
    sidebarCollapsed: false,
    user: null,
    stats: null,
    currentWorkspace: null,
    organizations: [],
    loading: true,
  });
  return store;
}

describe("app-store", () => {
  beforeEach(() => {
    createFreshStore();
  });

  describe("theme", () => {
    it("starts with system theme", () => {
      expect(useAppStore.getState().theme).toBe("system");
    });

    it("sets theme to light", () => {
      useAppStore.getState().setTheme("light");
      expect(useAppStore.getState().theme).toBe("light");
    });

    it("sets theme to dark", () => {
      useAppStore.getState().setTheme("dark");
      expect(useAppStore.getState().theme).toBe("dark");
    });

    it("switches between themes", () => {
      const store = useAppStore.getState();
      store.setTheme("light");
      store.setTheme("dark");
      expect(useAppStore.getState().theme).toBe("dark");
    });
  });

  describe("sidebar", () => {
    it("starts expanded", () => {
      expect(useAppStore.getState().sidebarCollapsed).toBe(false);
    });

    it("toggles sidebar collapsed state", () => {
      useAppStore.getState().toggleSidebar();
      expect(useAppStore.getState().sidebarCollapsed).toBe(true);
    });

    it("toggles sidebar back to expanded", () => {
      const store = useAppStore.getState();
      store.toggleSidebar();
      store.toggleSidebar();
      expect(useAppStore.getState().sidebarCollapsed).toBe(false);
    });

    it("sets sidebar collapsed explicitly", () => {
      useAppStore.getState().setSidebarCollapsed(true);
      expect(useAppStore.getState().sidebarCollapsed).toBe(true);
    });
  });

  describe("user", () => {
    it("starts with null user", () => {
      expect(useAppStore.getState().user).toBeNull();
    });

    it("sets user profile", () => {
      const user = {
        id: "1",
        name: "Test User",
        email: "test@example.com",
        role: "admin",
        preferences: {
          theme: "system" as Theme,
          sidebarCollapsed: false,
          fontSize: "medium" as const,
          reducedMotion: false,
        },
      };
      useAppStore.getState().setUser(user);
      expect(useAppStore.getState().user).toEqual(user);
    });

    it("clears user to null", () => {
      const user = {
        id: "1",
        name: "Test",
        email: "test@test.com",
        role: "user",
        preferences: {
          theme: "system" as Theme,
          sidebarCollapsed: false,
          fontSize: "medium" as const,
          reducedMotion: false,
        },
      };
      useAppStore.getState().setUser(user);
      useAppStore.getState().setUser(null);
      expect(useAppStore.getState().user).toBeNull();
    });
  });

  describe("stats", () => {
    it("starts with null stats", () => {
      expect(useAppStore.getState().stats).toBeNull();
    });

    it("sets dashboard stats", () => {
      const stats = {
        activeProjects: 5,
        activeAgents: 12,
        runningWorkflows: 3,
        totalTools: 24,
        activeExtensions: 8,
        platformHealth: "healthy" as const,
        uptime: 99.9,
        alerts: 2,
      };
      useAppStore.getState().setStats(stats);
      expect(useAppStore.getState().stats).toEqual(stats);
    });
  });

  describe("workspace", () => {
    it("starts with null workspace", () => {
      expect(useAppStore.getState().currentWorkspace).toBeNull();
    });

    it("sets current workspace", () => {
      const workspace = {
        id: "w1",
        name: "Production",
        description: "Prod workspace",
        environment: "production" as const,
        organizationId: "org1",
        projectCount: 10,
        activeAgentCount: 5,
        lastActivity: new Date(),
      };
      useAppStore.getState().setCurrentWorkspace(workspace);
      expect(useAppStore.getState().currentWorkspace).toEqual(workspace);
    });
  });

  describe("organizations", () => {
    it("starts with empty organizations", () => {
      expect(useAppStore.getState().organizations).toEqual([]);
    });

    it("sets organizations list", () => {
      const orgs = [
        { id: "org1", name: "Org A", slug: "org-a", description: "", memberCount: 5, workspaceCount: 2 },
        { id: "org2", name: "Org B", slug: "org-b", description: "", memberCount: 3, workspaceCount: 1 },
      ];
      useAppStore.getState().setOrganizations(orgs);
      expect(useAppStore.getState().organizations).toHaveLength(2);
      expect(useAppStore.getState().organizations[0].name).toBe("Org A");
    });
  });

  describe("loading", () => {
    it("starts with loading true", () => {
      expect(useAppStore.getState().loading).toBe(true);
    });

    it("sets loading state", () => {
      useAppStore.getState().setLoading(false);
      expect(useAppStore.getState().loading).toBe(false);
    });
  });
});
