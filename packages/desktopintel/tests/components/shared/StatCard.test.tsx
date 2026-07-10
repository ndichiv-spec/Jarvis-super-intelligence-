import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard } from "@/components/shared/stat-card";
import { Activity } from "lucide-react";

describe("StatCard", () => {
  it("renders title and value", () => {
    render(<StatCard title="CPU Usage" value="45%" />);
    expect(screen.getByText("CPU Usage")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<StatCard title="Memory" value="2.1 GB" description="of 8 GB" />);
    expect(screen.getByText("2.1 GB")).toBeInTheDocument();
    expect(screen.getByText("of 8 GB")).toBeInTheDocument();
  });

  it("renders trend with positive color", () => {
    render(<StatCard title="Uptime" value="99.9%" trend={{ value: "+0.5%", positive: true }} />);
    expect(screen.getByText("+0.5%")).toHaveClass("text-status-success");
  });

  it("renders trend with negative color", () => {
    render(<StatCard title="Errors" value="12" trend={{ value: "+3", positive: false }} />);
    expect(screen.getByText("+3")).toHaveClass("text-status-error");
  });

  it("renders icon when provided", () => {
    const { container } = render(<StatCard title="Active" value="5" icon={Activity} />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("applies className prop", () => {
    const { container } = render(<StatCard title="Test" value="1" className="custom-card" />);
    expect(container.firstChild).toHaveClass("custom-card");
  });
});
