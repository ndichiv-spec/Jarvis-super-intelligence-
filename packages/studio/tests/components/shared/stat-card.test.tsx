import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Activity } from "lucide-react";
import { StatCard } from "@/components/shared/stat-card";

describe("StatCard", () => {
  it("renders title and value", () => {
    render(<StatCard title="Active Projects" value={42} icon={Activity} />);
    expect(screen.getByText("Active Projects")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("renders string value", () => {
    render(<StatCard title="Status" value="Healthy" icon={Activity} />);
    expect(screen.getByText("Healthy")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(
      <StatCard title="Uptime" value="99.9%" icon={Activity} description="Last 30 days" />,
    );
    expect(screen.getByText("Last 30 days")).toBeInTheDocument();
  });

  it("does not render description when not provided", () => {
    render(<StatCard title="Uptime" value="99.9%" icon={Activity} />);
    expect(screen.queryByText("Last 30 days")).not.toBeInTheDocument();
  });

  it("renders positive trend", () => {
    render(
      <StatCard title="Agents" value={15} icon={Activity} trend={{ value: 12, positive: true }} />,
    );
    expect(screen.getByText("+12%")).toBeInTheDocument();
    expect(screen.getByText("+12%")).toHaveClass("text-status-success");
  });

  it("renders negative trend", () => {
    render(
      <StatCard title="Errors" value={3} icon={Activity} trend={{ value: 8, positive: false }} />,
    );
    expect(screen.getByText("8%")).toBeInTheDocument();
    expect(screen.getByText("8%")).toHaveClass("text-status-error");
  });

  it("renders icon container", () => {
    render(<StatCard title="Test" value={1} icon={Activity} />);
    const iconContainer = screen.getByText("Test").closest("div")?.parentElement;
    expect(iconContainer?.querySelector("svg")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <StatCard title="Test" value={1} icon={Activity} className="custom-card" />,
    );
    expect(container.firstChild).toHaveClass("custom-card");
  });
});
