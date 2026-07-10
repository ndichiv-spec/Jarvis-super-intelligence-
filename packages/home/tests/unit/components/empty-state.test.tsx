import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";

describe("EmptyState", () => {
  it("renders title", () => {
    render(<EmptyState title="Nothing here" />);
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<EmptyState title="Empty" description="This is empty" />);
    expect(screen.getByText("This is empty")).toBeInTheDocument();
  });

  it("renders action when provided", () => {
    render(<EmptyState title="Empty" action={<Button>Create</Button>} />);
    expect(screen.getByText("Create")).toBeInTheDocument();
  });
});
