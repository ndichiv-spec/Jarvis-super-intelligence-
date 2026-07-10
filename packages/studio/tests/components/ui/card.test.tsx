import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

describe("Card", () => {
  it("renders children content", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders with card class", () => {
    render(<Card>Content</Card>);
    expect(screen.getByText("Content")).toHaveClass("rounded-xl");
  });

  it("applies custom className", () => {
    render(<Card className="custom-card">Styled</Card>);
    expect(screen.getByText("Styled")).toHaveClass("custom-card");
  });
});

describe("CardHeader", () => {
  it("renders children", () => {
    render(<CardHeader>Header content</CardHeader>);
    expect(screen.getByText("Header content")).toBeInTheDocument();
  });

  it("renders with correct layout classes", () => {
    render(<CardHeader>Header</CardHeader>);
    expect(screen.getByText("Header")).toHaveClass("flex");
  });
});

describe("CardTitle", () => {
  it("renders as h3 element", () => {
    render(<CardTitle>Title</CardTitle>);
    const heading = screen.getByText("Title");
    expect(heading.tagName).toBe("H3");
  });

  it("renders with font-semibold class", () => {
    render(<CardTitle>Title</CardTitle>);
    expect(screen.getByText("Title")).toHaveClass("font-semibold");
  });
});

describe("CardDescription", () => {
  it("renders description text", () => {
    render(<CardDescription>Description text</CardDescription>);
    expect(screen.getByText("Description text")).toBeInTheDocument();
  });

  it("renders with muted text class", () => {
    render(<CardDescription>Desc</CardDescription>);
    expect(screen.getByText("Desc")).toHaveClass("text-muted-foreground");
  });
});

describe("CardContent", () => {
  it("renders children", () => {
    render(<CardContent>Content body</CardContent>);
    expect(screen.getByText("Content body")).toBeInTheDocument();
  });
});

describe("CardFooter", () => {
  it("renders children", () => {
    render(<CardFooter>Footer</CardFooter>);
    expect(screen.getByText("Footer")).toBeInTheDocument();
  });
});

describe("Card compound", () => {
  it("renders a complete card with all sub-components", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card description</CardDescription>
        </CardHeader>
        <CardContent>Main content area</CardContent>
        <CardFooter>Footer actions</CardFooter>
      </Card>,
    );

    expect(screen.getByText("Card Title")).toBeInTheDocument();
    expect(screen.getByText("Card description")).toBeInTheDocument();
    expect(screen.getByText("Main content area")).toBeInTheDocument();
    expect(screen.getByText("Footer actions")).toBeInTheDocument();
  });
});
