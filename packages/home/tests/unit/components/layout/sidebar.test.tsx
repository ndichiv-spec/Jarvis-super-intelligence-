import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { Sidebar } from "@/components/layout/sidebar";
import { useAppStore } from "@/stores/app-store";

beforeEach(() => {
  useAppStore.setState({ sidebarCollapsed: false, notifications: [], unreadCount: 0, theme: "system", user: null, stats: null, loading: false });
});

describe("Sidebar", () => {
  it("renders navigation items", () => {
    render(<Sidebar />);
    expect(screen.getByText("JARVIS Home")).toBeInTheDocument();
  });

  it("renders main navigation links", () => {
    render(<Sidebar />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Workspace")).toBeInTheDocument();
    expect(screen.getByText("Projects")).toBeInTheDocument();
  });

  it("renders collapsed state", () => {
    useAppStore.setState({ sidebarCollapsed: true });
    render(<Sidebar />);
    expect(screen.getByText("JH")).toBeInTheDocument();
  });

  it("renders notification badge with unread count", () => {
    useAppStore.setState({
      notifications: [
        { id: "1", type: "info", title: "Test", read: false, createdAt: new Date() },
        { id: "2", type: "info", title: "Test2", read: false, createdAt: new Date() },
      ],
      unreadCount: 2,
    });
    render(<Sidebar />);
    expect(screen.getByText("2")).toBeInTheDocument();
  });
});
