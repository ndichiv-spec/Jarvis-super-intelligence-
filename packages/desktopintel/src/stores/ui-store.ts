"use client";

import { create } from "zustand";

interface UIStore {
  sidebarOpen: boolean;
  notificationPanelOpen: boolean;
  commandPaletteOpen: boolean;
  settingsDialogOpen: boolean;
  permissionDialogOpen: boolean;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setNotificationPanelOpen: (open: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setSettingsDialogOpen: (open: boolean) => void;
  setPermissionDialogOpen: (open: boolean) => void;
  closeAllModals: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  notificationPanelOpen: false,
  commandPaletteOpen: false,
  settingsDialogOpen: false,
  permissionDialogOpen: false,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setNotificationPanelOpen: (open) => set({ notificationPanelOpen: open }),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
  setSettingsDialogOpen: (open) => set({ settingsDialogOpen: open }),
  setPermissionDialogOpen: (open) => set({ permissionDialogOpen: open }),
  closeAllModals: () => set({
    notificationPanelOpen: false,
    commandPaletteOpen: false,
    settingsDialogOpen: false,
    permissionDialogOpen: false,
  }),
}));
