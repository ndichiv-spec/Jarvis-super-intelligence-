import { describe, it, expect } from "vitest";
import {
  cn,
  formatRelativeTime,
  truncate,
  formatBytes,
  formatDuration,
  formatUptime,
  getPermissionLabel,
  getPermissionDescription,
} from "@/lib/utils";

describe("cn", () => {
  it("merges tailwind classes", () => {
    expect(cn("px-4", "py-2")).toBe("px-4 py-2");
  });

  it("last conflicting class wins", () => {
    expect(cn("px-4", "px-6")).toBe("px-6");
  });
});

describe("formatRelativeTime", () => {
  it('returns "just now" for < 1 minute', () => {
    expect(formatRelativeTime(new Date(Date.now() - 30000).toISOString())).toBe("just now");
  });

  it("returns minutes ago", () => {
    expect(formatRelativeTime(new Date(Date.now() - 5 * 60000).toISOString())).toBe("5m ago");
  });

  it("returns hours ago", () => {
    expect(formatRelativeTime(new Date(Date.now() - 3 * 3600000).toISOString())).toBe("3h ago");
  });

  it("returns days ago", () => {
    expect(formatRelativeTime(new Date(Date.now() - 4 * 86400000).toISOString())).toBe("4d ago");
  });
});

describe("truncate", () => {
  it("returns full string when within length", () => {
    expect(truncate("hello", 10)).toBe("hello");
  });

  it("truncates with ellipsis when longer", () => {
    expect(truncate("hello world", 5)).toBe("hello...");
  });

  it("returns string unchanged when equal to length", () => {
    expect(truncate("hello", 5)).toBe("hello");
  });
});

describe("formatBytes", () => {
  it("formats 0 bytes", () => {
    expect(formatBytes(0)).toBe("0 B");
  });

  it("formats bytes", () => {
    expect(formatBytes(500)).toBe("500 B");
  });

  it("formats KB", () => {
    expect(formatBytes(2048)).toBe("2 KB");
  });

  it("formats MB", () => {
    expect(formatBytes(5242880)).toBe("5 MB");
  });

  it("formats GB", () => {
    expect(formatBytes(1073741824)).toBe("1 GB");
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
});

describe("formatUptime", () => {
  it("formats less than a minute", () => {
    expect(formatUptime(30)).toBe("<1m");
  });

  it("formats minutes only", () => {
    expect(formatUptime(125)).toBe("2m");
  });

  it("formats hours and minutes", () => {
    expect(formatUptime(3660)).toBe("1h 1m");
  });

  it("formats days and hours", () => {
    expect(formatUptime(90000)).toBe("1d 1h");
  });
});

describe("getPermissionLabel", () => {
  it("returns label for known permissions", () => {
    expect(getPermissionLabel("file:read")).toBe("Read Files");
    expect(getPermissionLabel("clipboard:write")).toBe("Write Clipboard");
    expect(getPermissionLabel("camera:access")).toBe("Camera Access");
    expect(getPermissionLabel("screen:capture")).toBe("Screen Capture");
    expect(getPermissionLabel("integration:launch")).toBe("Launch Integrations");
  });

  it("returns the key for unknown permissions", () => {
    expect(getPermissionLabel("unknown:perm")).toBe("unknown:perm");
  });
});

describe("getPermissionDescription", () => {
  it("returns description for known permissions", () => {
    expect(getPermissionDescription("file:read")).toBe("Read files from selected locations");
    expect(getPermissionDescription("clipboard:write")).toBe("Copy content to your clipboard");
    expect(getPermissionDescription("camera:access")).toBe("Access your camera for capture");
    expect(getPermissionDescription("device:info")).toBe("Access device information");
  });

  it("returns the key for unknown permissions", () => {
    expect(getPermissionDescription("unknown:perm")).toBe("unknown:perm");
  });
});
