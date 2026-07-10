import { describe, it, expect } from "vitest";
import { cn, formatRelativeTime, truncate } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });

  it("merges tailwind classes correctly", () => {
    expect(cn("px-4", "px-2")).toBe("px-2");
  });
});

describe("formatRelativeTime", () => {
  it('returns "just now" for less than 1 minute', () => {
    expect(formatRelativeTime(new Date())).toBe("just now");
  });

  it("returns minutes for < 60 minutes", () => {
    const date = new Date(Date.now() - 5 * 60000);
    expect(formatRelativeTime(date)).toBe("5m ago");
  });

  it("returns hours for < 24 hours", () => {
    const date = new Date(Date.now() - 3 * 3600000);
    expect(formatRelativeTime(date)).toBe("3h ago");
  });

  it("returns days for < 7 days", () => {
    const date = new Date(Date.now() - 2 * 86400000);
    expect(formatRelativeTime(date)).toBe("2d ago");
  });

  it("returns formatted date for >= 7 days", () => {
    const date = new Date("2024-01-15");
    expect(formatRelativeTime(date)).toBe(date.toLocaleDateString());
  });
});

describe("truncate", () => {
  it("returns string as-is if within length", () => {
    expect(truncate("hello", 10)).toBe("hello");
  });

  it("truncates and adds ellipsis", () => {
    expect(truncate("hello world", 5)).toBe("hello...");
  });
});
