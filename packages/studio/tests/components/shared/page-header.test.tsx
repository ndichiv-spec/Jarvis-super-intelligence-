import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";

describe("PageHeader", () => {
  it("renders title", () => {
    render(<PageHeader title="Dashboard" />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("renders title as h1", () => {
    render(<PageHeader title="Settings" />);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toHaveTextContent("Settings");
  });

  it("renders description when provided", () => {
    render(<PageHeader title="Dashboard" description="View your stats" />);
    expect(screen.getByText("View your stats")).toBeInTheDocument();
  });

  it("does not render description when omitted", () => {
    render(<PageHeader title="Dashboard" />);
    expect(screen.queryByText("View your stats")).not.toBeInTheDocument();
  });

  it("renders actions when provided", () => {
    render(
      <PageHeader
        title="Users"
        actions={<Button>Add User</Button>}
      />,
    );
    expect(screen.getByRole("button", { name: "Add User" })).toBeInTheDocument();
  });

  it("does not render actions wrapper when omitted", () => {
    const { container } = render(<PageHeader title="Users" />);
    expect(container.querySelector(".gap-2")).not.toBeInTheDocument();
  });

  it("renders multiple actions", () => {
    render(
      <PageHeader
        title="Projects"
        actions={
          <>
            <Button>New</Button>
            <Button variant="outline">Import</Button>
          </>
        }
      />,
    );
    expect(screen.getByRole("button", { name: "New" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Import" })).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <PageHeader title="Title" className="custom-header" />,
    );
    expect(container.firstChild).toHaveClass("custom-header");
  });
});
