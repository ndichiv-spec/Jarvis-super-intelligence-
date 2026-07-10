import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

describe("Card", () => {
  it("renders with children", () => {
    render(<Card><p>card content</p></Card>);
    expect(screen.getByText("card content")).toBeInTheDocument();
  });

  it("CardHeader renders with className", () => {
    const { container } = render(<CardHeader className="custom-header" />);
    expect(container.firstChild).toHaveClass("custom-header");
  });

  it("CardTitle renders as h3", () => {
    render(<CardTitle>Title Text</CardTitle>);
    const heading = screen.getByRole("heading", { level: 3 });
    expect(heading).toHaveTextContent("Title Text");
  });

  it("CardContent renders children", () => {
    render(<CardContent><span>content child</span></CardContent>);
    expect(screen.getByText("content child")).toBeInTheDocument();
  });

  it("nested composition works", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Composed Title</CardTitle>
        </CardHeader>
        <CardContent>Body text</CardContent>
      </Card>,
    );
    expect(screen.getByRole("heading", { level: 3 })).toHaveTextContent("Composed Title");
    expect(screen.getByText("Body text")).toBeInTheDocument();
  });
});
