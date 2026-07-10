import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/shared/empty-state";
import { AlertCircle } from "lucide-react";

describe("EmptyState", () => {
  it("renders title", () => {
    render(<EmptyState title="No items found" />);
    expect(screen.getByText("No items found")).toBeInTheDocument();
  });

  it("renders default icon (Inbox)", () => {
    const { container } = render(<EmptyState title="Empty" />);
    const iconContainer = container.querySelector(".rounded-full");
    expect(iconContainer).toBeInTheDocument();
    expect(iconContainer?.querySelector("svg")).toBeInTheDocument();
  });

  it("renders custom icon", () => {
    const { container } = render(<EmptyState title="Error" icon={AlertCircle} />);
    const iconContainer = container.querySelector(".rounded-full");
    expect(iconContainer?.querySelector("svg")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(
      <EmptyState title="No data" description="Add some data to get started." />,
    );
    expect(screen.getByText("Add some data to get started.")).toBeInTheDocument();
  });

  it("does not render description when omitted", () => {
    render(<EmptyState title="No data" />);
    expect(screen.queryByText("Add some data to get started.")).not.toBeInTheDocument();
  });

  it("renders action when provided", () => {
    render(
      <EmptyState
        title="No projects"
        action={<Button>Create Project</Button>}
      />,
    );
    expect(screen.getByRole("button", { name: "Create Project" })).toBeInTheDocument();
  });

  it("does not render action container when omitted", () => {
    render(<EmptyState title="No projects" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <EmptyState title="Empty" className="custom-empty" />,
    );
    expect(container.firstChild).toHaveClass("custom-empty");
  });

  it("renders title as h3", () => {
    render(<EmptyState title="Section title" />);
    const heading = screen.getByText("Section title");
    expect(heading.tagName).toBe("H3");
  });
});
