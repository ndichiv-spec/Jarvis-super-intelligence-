import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { StatusDot } from "@/components/shared/status-dot";

describe("StatusDot", () => {
  function getStatusSpan(status: string) {
    const { container } = render(<StatusDot status={status as any} />);
    return container.firstChild as HTMLElement;
  }

  describe("success colors", () => {
    it.each(["healthy", "active", "success", "available", "published"])(
      "renders %s with bg-status-success",
      (status) => {
        expect(getStatusSpan(status)).toHaveClass("bg-status-success");
      },
    );
  });

  describe("warning colors", () => {
    it.each(["degraded", "warning", "busy", "maintenance"])(
      "renders %s with bg-status-warning",
      (status) => {
        expect(getStatusSpan(status)).toHaveClass("bg-status-warning");
      },
    );
  });

  describe("pending colors", () => {
    it.each(["pending", "idle", "draft"])(
      "renders %s with bg-status-pending",
      (status) => {
        expect(getStatusSpan(status)).toHaveClass("bg-status-pending");
      },
    );
  });

  describe("error colors", () => {
    it.each(["critical", "error", "suspended"])(
      "renders %s with bg-status-error",
      (status) => {
        expect(getStatusSpan(status)).toHaveClass("bg-status-error");
      },
    );
  });

  describe("muted colors", () => {
    it.each(["inactive", "disabled", "archived"])(
      "renders %s with bg-muted-foreground",
      (status) => {
        expect(getStatusSpan(status)).toHaveClass("bg-muted-foreground");
      },
    );
  });

  it("renders info status with bg-status-info", () => {
    expect(getStatusSpan("running")).toHaveClass("bg-status-info");
  });

  it("uses fallback class for unknown status", () => {
    expect(getStatusSpan("unknown")).toHaveClass("bg-muted-foreground");
  });

  it("renders as a span element", () => {
    const { container } = render(<StatusDot status="active" />);
    expect(container.firstChild?.nodeName).toBe("SPAN");
  });

  it("applies custom className", () => {
    const { container } = render(<StatusDot status="active" className="custom-dot" />);
    expect(container.firstChild).toHaveClass("custom-dot");
  });

  it("has inline-block and rounded classes", () => {
    const el = getStatusSpan("active");
    expect(el).toHaveClass("inline-block", "rounded-full");
  });
});
