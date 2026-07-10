import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { Header } from "@/components/layout/header";
import { useAppStore } from "@/stores/app-store";

beforeEach(() => {
  useAppStore.setState({ sidebarCollapsed: false, notifications: [], unreadCount: 0, theme: "system", user: null, stats: null, loading: false });
});

describe("Header", () => {
  it("renders search bar", () => {
    render(<Header />);
    expect(screen.getByPlaceholderText("Search...")).toBeInTheDocument();
  });

  it("renders notification button", () => {
    render(<Header />);
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });

  it("renders theme toggle", () => {
    render(<Header />);
    expect(screen.getByRole("button", { name: /toggle theme/i })).toBeInTheDocument();
  });

  it("renders user menu when user is set", () => {
    useAppStore.setState({
      user: { id: "1", name: "John", email: "john@test.com", avatar: null, role: "user", preferences: { theme: "system", language: "en" } },
    });
    render(<Header />);
    expect(screen.getByText("John")).toBeInTheDocument();
  });
});
