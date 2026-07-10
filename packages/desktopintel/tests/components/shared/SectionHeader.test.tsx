import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SectionHeader } from "@/components/shared/section-header";

describe("SectionHeader", () => {
  it("renders title", () => {
    render(<SectionHeader title="Section Title" />);
    expect(screen.getByText("Section Title")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<SectionHeader title="Title" description="Descriptive text" />);
    expect(screen.getByText("Descriptive text")).toBeInTheDocument();
  });

  it("renders action element when provided", () => {
    render(
      <SectionHeader
        title="Manage"
        action={<button>Action</button>}
      />,
    );
    expect(screen.getByRole("button", { name: "Action" })).toBeInTheDocument();
  });
});
