"use client";

import { create } from "zustand";

type PanelId = "explorer" | "outline" | "console" | "properties" | "minimap";

interface PanelState {
  openPanels: PanelId[];
  activeConsoleTab: "logs" | "diagnostics" | "validation" | "tasks" | "events";
  selectedNodeId: string | null;
  selectedEdgeId: string | null;

  togglePanel: (panel: PanelId) => void;
  setPanelOpen: (panel: PanelId, open: boolean) => void;
  setActiveConsoleTab: (tab: PanelState["activeConsoleTab"]) => void;
  setSelectedNodeId: (id: string | null) => void;
  setSelectedEdgeId: (id: string | null) => void;
}

export const useUIStore = create<PanelState>((set) => ({
  openPanels: ["explorer", "outline"],
  activeConsoleTab: "logs",
  selectedNodeId: null,
  selectedEdgeId: null,

  togglePanel: (panel) =>
    set((s) => ({
      openPanels: s.openPanels.includes(panel)
        ? s.openPanels.filter((p) => p !== panel)
        : [...s.openPanels, panel],
    })),

  setPanelOpen: (panel, open) =>
    set((s) => ({
      openPanels: open
        ? [...s.openPanels, panel]
        : s.openPanels.filter((p) => p !== panel),
    })),

  setActiveConsoleTab: (activeConsoleTab) => set({ activeConsoleTab }),
  setSelectedNodeId: (selectedNodeId) => set({ selectedNodeId }),
  setSelectedEdgeId: (selectedEdgeId) => set({ selectedEdgeId }),
}));
