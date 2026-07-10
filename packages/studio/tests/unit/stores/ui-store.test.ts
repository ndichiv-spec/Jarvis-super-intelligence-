import { describe, it, expect, beforeEach } from "vitest";
import { useUIStore } from "@/stores/ui-store";

function createFreshStore() {
  const store = useUIStore;
  store.setState({
    openPanels: ["explorer", "outline"],
    activeConsoleTab: "logs",
    selectedNodeId: null,
    selectedEdgeId: null,
  });
  return store;
}

describe("ui-store", () => {
  beforeEach(() => {
    createFreshStore();
  });

  describe("panels", () => {
    it("starts with explorer and outline open", () => {
      expect(useUIStore.getState().openPanels).toEqual(["explorer", "outline"]);
    });

    it("toggles a panel on", () => {
      useUIStore.getState().togglePanel("console");
      expect(useUIStore.getState().openPanels).toContain("console");
    });

    it("toggles a panel off", () => {
      useUIStore.getState().togglePanel("explorer");
      expect(useUIStore.getState().openPanels).not.toContain("explorer");
    });

    it("toggles the same panel on and off", () => {
      useUIStore.getState().togglePanel("minimap");
      useUIStore.getState().togglePanel("minimap");
      expect(useUIStore.getState().openPanels).not.toContain("minimap");
    });

    it("sets panel open to true", () => {
      useUIStore.getState().setPanelOpen("properties", true);
      expect(useUIStore.getState().openPanels).toContain("properties");
    });

    it("sets panel open to false", () => {
      useUIStore.getState().setPanelOpen("outline", false);
      expect(useUIStore.getState().openPanels).not.toContain("outline");
    });

    it("adds panel even if already open (no dedup)", () => {
      useUIStore.getState().setPanelOpen("explorer", true);
      expect(useUIStore.getState().openPanels.filter((p) => p === "explorer")).toHaveLength(2);
    });
  });

  describe("console tab", () => {
    it("starts with logs tab", () => {
      expect(useUIStore.getState().activeConsoleTab).toBe("logs");
    });

    it("sets active console tab", () => {
      useUIStore.getState().setActiveConsoleTab("diagnostics");
      expect(useUIStore.getState().activeConsoleTab).toBe("diagnostics");
    });

    it("switches between all console tabs", () => {
      const tabs = ["diagnostics", "validation", "tasks", "events"] as const;
      for (const tab of tabs) {
        useUIStore.getState().setActiveConsoleTab(tab);
        expect(useUIStore.getState().activeConsoleTab).toBe(tab);
      }
    });
  });

  describe("node selection", () => {
    it("starts with no selected node", () => {
      expect(useUIStore.getState().selectedNodeId).toBeNull();
    });

    it("selects a node", () => {
      useUIStore.getState().setSelectedNodeId("node-1");
      expect(useUIStore.getState().selectedNodeId).toBe("node-1");
    });

    it("deselects a node", () => {
      useUIStore.getState().setSelectedNodeId("node-1");
      useUIStore.getState().setSelectedNodeId(null);
      expect(useUIStore.getState().selectedNodeId).toBeNull();
    });

    it("changes selected node", () => {
      useUIStore.getState().setSelectedNodeId("node-1");
      useUIStore.getState().setSelectedNodeId("node-2");
      expect(useUIStore.getState().selectedNodeId).toBe("node-2");
    });
  });

  describe("edge selection", () => {
    it("starts with no selected edge", () => {
      expect(useUIStore.getState().selectedEdgeId).toBeNull();
    });

    it("selects an edge", () => {
      useUIStore.getState().setSelectedEdgeId("edge-1");
      expect(useUIStore.getState().selectedEdgeId).toBe("edge-1");
    });

    it("clears edge selection", () => {
      useUIStore.getState().setSelectedEdgeId("edge-1");
      useUIStore.getState().setSelectedEdgeId(null);
      expect(useUIStore.getState().selectedEdgeId).toBeNull();
    });
  });
});
