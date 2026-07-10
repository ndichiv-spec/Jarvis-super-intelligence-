import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EmptyState } from "@/components/shared/empty-state";
import { Activity } from "lucide-react";

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(<EmptyState title="No data" description="There is nothing to display yet." />);
    expect(screen.getByText("No data")).toBeInTheDocument();
    expect(screen.getByText("There is nothing to display yet.")).toBeInTheDocument();
  });

  it("renders default icon (Inbox)", () => {
    const { container } = render(<EmptyState title="Empty" description="Nothing here" />);
    const svgs = container.querySelectorAll("svg");
    expect(svgs.length).toBeGreaterThan(0);
  });

  it("renders custom icon when provided", () => {
    const { container } = render(<EmptyState title="Empty" description="No activity" icon={Activity} />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("renders action element when provided", () => {
    render(
      <EmptyState
        title="No items"
        description="Create a new item to get started"
        action={<button>Create</button>}
      />,
    );
    expect(screen.getByRole("button", { name: "Create" })).toBeInTheDocument();
  });
});
