import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { StatusDot } from "@/components/shared/status-dot";

describe("StatusDot", () => {
  it("renders with healthy status", () => {
    const { container } = render(<StatusDot status="healthy" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("renders with error status", () => {
    const { container } = render(<StatusDot status="error" />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it("renders with active status", () => {
    const { container } = render(<StatusDot status="active" />);
    expect(container.firstChild).toBeInTheDocument();
  });
});
