import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MainLayout } from "@/components/layout/main-layout";
import { useAppStore } from "@/stores/app-store";

beforeEach(() => {
  useAppStore.setState({ sidebarCollapsed: false, notifications: [], unreadCount: 0, theme: "system", user: null, stats: null, loading: false });
});

describe("MainLayout", () => {
  it("renders children", () => {
    render(<MainLayout>Page content</MainLayout>);
    expect(screen.getByText("Page content")).toBeInTheDocument();
  });

  it("renders sidebar and header", () => {
    render(<MainLayout>Content</MainLayout>);
    expect(screen.getByText("JARVIS Home")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search...")).toBeInTheDocument();
  });
});
