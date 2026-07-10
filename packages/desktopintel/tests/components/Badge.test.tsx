import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { Badge } from "@/components/ui/badge";

describe("Badge", () => {
  it("renders with default variant", () => {
    const { container } = render(<Badge>Default</Badge>);
    expect(container.firstChild).toHaveClass("bg-primary/10");
  });

  it("applies variant classes", () => {
    const { container, rerender } = render(<Badge variant="secondary">Secondary</Badge>);
    expect(container.firstChild).toHaveClass("bg-secondary");
    rerender(<Badge variant="destructive">Destructive</Badge>);
    expect(container.firstChild).toHaveClass("bg-destructive/10");
    rerender(<Badge variant="outline">Outline</Badge>);
    expect(container.firstChild).toHaveClass("text-foreground");
    rerender(<Badge variant="success">Success</Badge>);
    expect(container.firstChild).toHaveClass("bg-emerald-100");
    rerender(<Badge variant="warning">Warning</Badge>);
    expect(container.firstChild).toHaveClass("bg-amber-100");
    rerender(<Badge variant="info">Info</Badge>);
    expect(container.firstChild).toHaveClass("bg-sky-100");
  });

  it("renders children text", () => {
    const { container } = render(<Badge>Active</Badge>);
    expect(container.firstChild).toHaveTextContent("Active");
  });

  it("applies className prop", () => {
    const { container } = render(<Badge className="custom-badge">Styled</Badge>);
    expect(container.firstChild).toHaveClass("custom-badge");
  });
});
