import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";

describe("button accessibility", () => {
  it("has button role by default", () => {
    render(<Button>Click</Button>);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("supports aria-label", () => {
    render(<Button aria-label="Close dialog">X</Button>);
    expect(screen.getByRole("button", { name: "Close dialog" })).toBeInTheDocument();
  });

  it("supports aria-pressed", () => {
    render(<Button aria-pressed="true">Toggle</Button>);
    expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "true");
  });

  it("supports aria-disabled via disabled prop", () => {
    render(<Button disabled>Saving</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("is focusable by default", () => {
    render(<Button>Focus me</Button>);
    const button = screen.getByRole("button");
    button.focus();
    expect(document.activeElement).toBe(button);
  });
});

describe("heading accessibility", () => {
  it("renders h1 as heading level 1", () => {
    render(<h1>Main title</h1>);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Main title");
  });

  it("renders h2 as heading level 2", () => {
    render(<h2>Section title</h2>);
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("Section title");
  });

  it("renders h3 as heading level 3", () => {
    render(<h3>Sub section</h3>);
    expect(screen.getByRole("heading", { level: 3 })).toHaveTextContent("Sub section");
  });

  it("supports multiple headings in hierarchy", () => {
    render(
      <div>
        <h1>Page Title</h1>
        <h2>Section A</h2>
        <h3>Sub-section</h3>
        <h2>Section B</h2>
      </div>,
    );
    const headings = screen.getAllByRole("heading");
    expect(headings).toHaveLength(4);
  });

  it("headings have accessible text content", () => {
    render(<h1 aria-label="Main Heading">Dashboard</h1>);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toHaveTextContent("Dashboard");
  });
});

describe("landmark accessibility", () => {
  it("renders navigation landmark", () => {
    render(<nav>Navigation</nav>);
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  it("renders main landmark", () => {
    render(<main>Main content</main>);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
