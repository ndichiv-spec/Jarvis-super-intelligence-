import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoadingScreen } from "@/components/shared/loading-screen";

describe("LoadingScreen", () => {
  const mockEvents = [
    { stage: "config" as const, status: "success" as const, timestamp: Date.now(), message: "Configuration loaded" },
  ];

  it("renders J logo", () => {
    render(<LoadingScreen stage="config" events={mockEvents} />);
    expect(screen.getByText("J")).toBeInTheDocument();
  });

  it("renders current stage label", () => {
    render(<LoadingScreen stage="gateway" events={mockEvents} />);
    expect(screen.getByText("Connecting to Gateway...")).toBeInTheDocument();
  });

  it("renders ready stage label", () => {
    render(<LoadingScreen stage="ready" events={mockEvents} />);
    expect(screen.getByText("Ready.")).toBeInTheDocument();
  });

  it("shows completed stage checkmark", () => {
    render(<LoadingScreen stage="gateway" events={mockEvents} />);
    expect(screen.getByText("✓")).toBeInTheDocument();
  });
});
