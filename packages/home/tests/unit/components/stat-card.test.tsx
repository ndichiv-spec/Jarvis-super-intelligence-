import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard } from "@/components/shared/stat-card";
import { Bot } from "lucide-react";

describe("StatCard", () => {
  it("renders title and value", () => {
    render(<StatCard title="Active Agents" value={8} icon={Bot} />);
    expect(screen.getByText("Active Agents")).toBeInTheDocument();
    expect(screen.getByText("8")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<StatCard title="Test" value={5} icon={Bot} description="Test description" />);
    expect(screen.getByText("Test description")).toBeInTheDocument();
  });

  it("renders positive trend", () => {
    render(<StatCard title="Test" value={5} icon={Bot} trend={{ value: 10, positive: true }} />);
    expect(screen.getByText("+10%")).toBeInTheDocument();
  });

  it("renders negative trend", () => {
    render(<StatCard title="Test" value={5} icon={Bot} trend={{ value: 5, positive: false }} />);
    expect(screen.getByText("-5%")).toBeInTheDocument();
  });
});
