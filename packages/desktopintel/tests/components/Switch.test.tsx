import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Switch } from "@/components/ui/switch";

describe("Switch", () => {
  it("renders as switch role", () => {
    render(<Switch />);
    expect(screen.getByRole("switch")).toBeInTheDocument();
  });

  it("toggles between checked/unchecked", () => {
    render(<Switch />);
    const sw = screen.getByRole("switch");
    expect(sw).toHaveAttribute("data-state", "unchecked");
    fireEvent.click(sw);
    expect(sw).toHaveAttribute("data-state", "checked");
    fireEvent.click(sw);
    expect(sw).toHaveAttribute("data-state", "unchecked");
  });

  it("applies className", () => {
    render(<Switch className="custom-switch" />);
    expect(screen.getByRole("switch")).toHaveClass("custom-switch");
  });

  it("disabled state", () => {
    render(<Switch disabled />);
    expect(screen.getByRole("switch")).toBeDisabled();
  });
});
