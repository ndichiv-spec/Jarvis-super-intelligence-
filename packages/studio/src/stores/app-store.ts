"use client";

import { create } from "zustand";
import type { Theme, UserProfile, DashboardStats, Workspace, Organization } from "@/types";

interface AppState {
  theme: Theme;
  sidebarCollapsed: boolean;
  user: UserProfile | null;
  stats: DashboardStats | null;
  currentWorkspace: Workspace | null;
  organizations: Organization[];
  loading: boolean;

  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setUser: (user: UserProfile | null) => void;
  setStats: (stats: DashboardStats | null) => void;
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  setOrganizations: (organizations: Organization[]) => void;
  setLoading: (loading: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  theme: "system",
  sidebarCollapsed: false,
  user: null,
  stats: null,
  currentWorkspace: null,
  organizations: [],
  loading: true,

  setTheme: (theme) => set({ theme }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
  setUser: (user) => set({ user }),
  setStats: (stats) => set({ stats }),
  setCurrentWorkspace: (currentWorkspace) => set({ currentWorkspace }),
  setOrganizations: (organizations) => set({ organizations }),
  setLoading: (loading) => set({ loading }),
}));
