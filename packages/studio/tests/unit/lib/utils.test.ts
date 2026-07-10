import { describe, it, expect } from "vitest";
import { cn, formatRelativeTime, truncate, formatBytes, formatDuration } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("px-4", "py-2")).toBe("px-4 py-2");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });

  it("merges tailwind classes correctly", () => {
    expect(cn("px-4", "px-6")).toBe("px-6");
  });

  it("handles empty input", () => {
    expect(cn()).toBe("");
  });
});

describe("formatRelativeTime", () => {
  it('returns "just now" for less than 1 minute', () => {
    expect(formatRelativeTime(new Date())).toBe("just now");
  });

  it("returns minutes ago format", () => {
    const date = new Date(Date.now() - 5 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe("5m ago");
  });

  it("returns hours ago format", () => {
    const date = new Date(Date.now() - 3 * 60 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe("3h ago");
  });

  it("returns days ago format", () => {
    const date = new Date(Date.now() - 4 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(date)).toBe("4d ago");
  });

  it("returns date string for older dates", () => {
    const date = new Date("2024-01-01");
    expect(formatRelativeTime(date)).toBe(date.toLocaleDateString());
  });
});

describe("truncate", () => {
  it("returns string unchanged when within length", () => {
    expect(truncate("hello", 10)).toBe("hello");
  });

  it("truncates and appends ellipsis", () => {
    expect(truncate("hello world this is long", 10)).toBe("hello worl...");
  });

  it("handles exact length", () => {
    expect(truncate("hello", 5)).toBe("hello");
  });

  it("handles empty string", () => {
    expect(truncate("", 5)).toBe("");
  });
});

describe("formatBytes", () => {
  it("formats 0 bytes", () => {
    expect(formatBytes(0)).toBe("0 B");
  });

  it("formats bytes", () => {
    expect(formatBytes(512)).toBe("512 B");
  });

  it("formats kilobytes", () => {
    expect(formatBytes(2048)).toBe("2 KB");
  });

  it("formats megabytes", () => {
    expect(formatBytes(5 * 1024 * 1024)).toBe("5 MB");
  });

  it("formats gigabytes", () => {
    expect(formatBytes(3 * 1024 * 1024 * 1024)).toBe("3 GB");
  });
});

describe("formatDuration", () => {
  it("formats seconds", () => {
    expect(formatDuration(5000)).toBe("5s");
  });

  it("formats minutes and seconds", () => {
    expect(formatDuration(125000)).toBe("2m 5s");
  });

  it("formats hours and minutes", () => {
    expect(formatDuration(3661000)).toBe("1h 1m");
  });

  it("handles zero", () => {
    expect(formatDuration(0)).toBe("0s");
  });

  it("formats exactly one minute", () => {
    expect(formatDuration(60000)).toBe("1m 0s");
  });
});
