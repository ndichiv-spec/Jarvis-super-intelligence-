import { describe, it, expect, beforeEach } from "vitest";
import { useAppStore } from "@/stores/app-store";

describe("AppStore", () => {
  beforeEach(() => {
    useAppStore.setState({
      theme: "system",
      sidebarCollapsed: false,
      notifications: [],
      unreadCount: 0,
      user: null,
      stats: null,
      loading: true,
    });
  });

  it("sets theme correctly", () => {
    useAppStore.getState().setTheme("dark");
    expect(useAppStore.getState().theme).toBe("dark");
  });

  it("toggles sidebar", () => {
    useAppStore.getState().toggleSidebar();
    expect(useAppStore.getState().sidebarCollapsed).toBe(true);
    useAppStore.getState().toggleSidebar();
    expect(useAppStore.getState().sidebarCollapsed).toBe(false);
  });

  it("sets sidebar collapsed directly", () => {
    useAppStore.getState().setSidebarCollapsed(true);
    expect(useAppStore.getState().sidebarCollapsed).toBe(true);
  });

  it("adds notification and increments unread count", () => {
    const notification = {
      id: "1",
      type: "platform" as const,
      title: "Test",
      message: "Test notification",
      severity: "info" as const,
      read: false,
      timestamp: new Date(),
    };
    useAppStore.getState().addNotification(notification);
    expect(useAppStore.getState().notifications).toHaveLength(1);
    expect(useAppStore.getState().unreadCount).toBe(1);
  });

  it("marks notification as read", () => {
    const notification = {
      id: "1",
      type: "platform" as const,
      title: "Test",
      message: "Test notification",
      severity: "info" as const,
      read: false,
      timestamp: new Date(),
    };
    useAppStore.getState().addNotification(notification);
    useAppStore.getState().markNotificationRead("1");
    expect(useAppStore.getState().notifications[0].read).toBe(true);
    expect(useAppStore.getState().unreadCount).toBe(0);
  });

  it("marks all notifications as read", () => {
    const n1 = { id: "1", type: "platform" as const, title: "T1", message: "M1", severity: "info" as const, read: false, timestamp: new Date() };
    const n2 = { id: "2", type: "agent" as const, title: "T2", message: "M2", severity: "warning" as const, read: false, timestamp: new Date() };
    useAppStore.getState().addNotification(n1);
    useAppStore.getState().addNotification(n2);
    useAppStore.getState().markAllNotificationsRead();
    expect(useAppStore.getState().notifications.every((n) => n.read)).toBe(true);
    expect(useAppStore.getState().unreadCount).toBe(0);
  });

  it("sets user", () => {
    const user = { id: "1", name: "Alex", email: "alex@test.com", role: "Dev", preferences: { theme: "system" as const, sidebarCollapsed: false, fontSize: "medium" as const, reducedMotion: false } };
    useAppStore.getState().setUser(user);
    expect(useAppStore.getState().user).toEqual(user);
  });

  it("sets stats", () => {
    const stats = { activeProjects: 5, activeAgents: 3, runningAutomations: 2, recentConversations: 10, memoryItems: 100, knowledgeDocuments: 50, unreadNotifications: 1, platformHealth: "healthy" as const, uptime: 99.9 };
    useAppStore.getState().setStats(stats);
    expect(useAppStore.getState().stats).toEqual(stats);
  });

  it("sets loading", () => {
    useAppStore.getState().setLoading(false);
    expect(useAppStore.getState().loading).toBe(false);
  });
});
