import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";

describe("PageHeader", () => {
  it("renders title", () => {
    render(<PageHeader title="Dashboard" />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<PageHeader title="Test" description="A description" />);
    expect(screen.getByText("A description")).toBeInTheDocument();
  });

  it("renders actions when provided", () => {
    render(<PageHeader title="Test" actions={<Button>Action</Button>} />);
    expect(screen.getByText("Action")).toBeInTheDocument();
  });
});
