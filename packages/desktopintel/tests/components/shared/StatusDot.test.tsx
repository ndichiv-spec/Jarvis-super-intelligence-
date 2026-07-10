import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusDot } from "@/components/shared/status-dot";

describe("StatusDot", () => {
  function renderDot(status: string) {
    return render(<StatusDot status={status as any} />).container.firstChild as HTMLElement;
  }

  it("renders healthy with bg-status-success", () => {
    expect(renderDot("healthy")).toHaveClass("bg-status-success");
  });

  it("renders connected with bg-status-success", () => {
    expect(renderDot("connected")).toHaveClass("bg-status-success");
  });

  it("renders synced with bg-status-success", () => {
    expect(renderDot("synced")).toHaveClass("bg-status-success");
  });

  it("renders active with bg-status-success", () => {
    expect(renderDot("active")).toHaveClass("bg-status-success");
  });

  it("renders enabled with bg-status-success", () => {
    expect(renderDot("enabled")).toHaveClass("bg-status-success");
  });

  it("renders degraded with bg-status-warning", () => {
    expect(renderDot("degraded")).toHaveClass("bg-status-warning");
  });

  it("renders syncing with bg-status-warning", () => {
    expect(renderDot("syncing")).toHaveClass("bg-status-warning");
  });

  it("renders pending with bg-status-warning", () => {
    expect(renderDot("pending")).toHaveClass("bg-status-warning");
  });

  it("renders error with bg-status-error", () => {
    expect(renderDot("error")).toHaveClass("bg-status-error");
  });

  it("renders disconnected with bg-status-error", () => {
    expect(renderDot("disconnected")).toHaveClass("bg-status-error");
  });

  it("renders offline with bg-status-error", () => {
    expect(renderDot("offline")).toHaveClass("bg-status-error");
  });

  it("renders inactive with bg-status-pending", () => {
    expect(renderDot("inactive")).toHaveClass("bg-status-pending");
  });

  it("renders disabled with bg-status-pending", () => {
    expect(renderDot("disabled")).toHaveClass("bg-status-pending");
  });

  it("applies aria-label", () => {
    render(<StatusDot status="healthy" />);
    expect(screen.getByLabelText("Status: healthy")).toBeInTheDocument();
  });

  it("applies className prop", () => {
    const el = renderDot("active");
    expect(el).toHaveClass("inline-block", "rounded-full");
  });
});
