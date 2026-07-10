import { create } from "zustand";
import type { Theme, Notification, UserProfile, DashboardStats } from "@/types";

interface AppState {
  theme: Theme;
  sidebarCollapsed: boolean;
  notifications: Notification[];
  unreadCount: number;
  user: UserProfile | null;
  stats: DashboardStats | null;
  loading: boolean;

  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  setUser: (user: UserProfile | null) => void;
  setStats: (stats: DashboardStats | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: "system",
  sidebarCollapsed: false,
  notifications: [],
  unreadCount: 0,
  user: null,
  stats: null,
  loading: true,

  setTheme: (theme) => set({ theme }),

  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),

  setNotifications: (notifications) =>
    set({
      notifications,
      unreadCount: notifications.filter((n) => !n.read).length,
    }),

  addNotification: (notification) =>
    set((s) => ({
      notifications: [notification, ...s.notifications],
      unreadCount: s.unreadCount + (notification.read ? 0 : 1),
    })),

  markNotificationRead: (id) =>
    set((s) => {
      const notifications = s.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n,
      );
      return {
        notifications,
        unreadCount: notifications.filter((n) => !n.read).length,
      };
    }),

  markAllNotificationsRead: () =>
    set((s) => ({
      notifications: s.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    })),

  setUser: (user) => set({ user }),
  setStats: (stats) => set({ stats }),
  setLoading: (loading) => set({ loading }),
}));
