import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SectionHeader } from "@/components/shared/section-header";

describe("SectionHeader", () => {
  it("renders title", () => {
    render(<SectionHeader title="My Section" />);
    expect(screen.getByText("My Section")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<SectionHeader title="Section" description="Section description" />);
    expect(screen.getByText("Section description")).toBeInTheDocument();
  });

  it("renders action link when provided", () => {
    render(<SectionHeader title="Section" action={{ label: "View All", href: "/all" }} />);
    expect(screen.getByText("View All")).toBeInTheDocument();
  });
});
