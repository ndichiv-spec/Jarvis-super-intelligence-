import { describe, it, expect } from "vitest";
import { commands } from "@/lib/commands";

describe("commands", () => {
  it("getRuntimeStatus returns expected shape", async () => {
    const result = await commands.getRuntimeStatus();
    expect(result).toHaveProperty("version");
    expect(result).toHaveProperty("startedAt");
    expect(result).toHaveProperty("uptime");
    expect(result).toHaveProperty("sessionId");
    expect(result).toHaveProperty("gatewayConnected");
    expect(result).toHaveProperty("capabilities");
  });

  it("getPermissions returns correct structure", async () => {
    const result = await commands.getPermissions();
    expect(result).toHaveProperty("granted");
    expect(result).toHaveProperty("pending");
    expect(result).toHaveProperty("history");
    expect(Array.isArray(result.granted)).toBe(true);
    expect(Array.isArray(result.pending)).toBe(true);
    expect(Array.isArray(result.history)).toBe(true);
  });

  it("granted permissions have correct shape", async () => {
    const { granted } = await commands.getPermissions();
    for (const g of granted) {
      expect(g).toHaveProperty("id");
      expect(g).toHaveProperty("permission");
      expect(g).toHaveProperty("resource");
      expect(g).toHaveProperty("grantedAt");
      expect(g).toHaveProperty("revoked");
    }
  });

  it("pending permissions have correct shape", async () => {
    const { pending } = await commands.getPermissions();
    for (const p of pending) {
      expect(p).toHaveProperty("id");
      expect(p).toHaveProperty("permission");
      expect(p).toHaveProperty("resource");
      expect(p).toHaveProperty("reason");
      expect(p).toHaveProperty("source");
      expect(p).toHaveProperty("requestedAt");
      expect(p).toHaveProperty("status");
    }
  });

  it("history events have correct shape", async () => {
    const { history } = await commands.getPermissions();
    for (const h of history) {
      expect(h).toHaveProperty("id");
      expect(h).toHaveProperty("permission");
      expect(h).toHaveProperty("action");
      expect(h).toHaveProperty("resource");
      expect(h).toHaveProperty("timestamp");
      expect(h).toHaveProperty("actor");
    }
  });

  it("getSyncStatus returns expected shape", async () => {
    const result = await commands.getSyncStatus();
    expect(result).toHaveProperty("state");
    expect(result).toHaveProperty("lastSyncAt");
    expect(result).toHaveProperty("pendingChanges");
    expect(result).toHaveProperty("conflicts");
    expect(result).toHaveProperty("modules");
    expect(Array.isArray(result.modules)).toBe(true);
  });

  it("getOfflineStatus returns expected shape", async () => {
    const result = await commands.getOfflineStatus();
    expect(result).toHaveProperty("enabled");
    expect(result).toHaveProperty("connected");
    expect(result).toHaveProperty("cachedConversations");
    expect(result).toHaveProperty("cachedKnowledge");
    expect(result).toHaveProperty("pendingActions");
    expect(result).toHaveProperty("storageUsed");
    expect(result).toHaveProperty("storageLimit");
  });

  it("getUpdateStatus returns expected shape", async () => {
    const result = await commands.getUpdateStatus();
    expect(result).toHaveProperty("currentVersion");
    expect(result).toHaveProperty("updateAvailable");
    expect(result).toHaveProperty("channel");
    expect(result).toHaveProperty("lastCheckedAt");
  });

  it("getDiagnostics returns expected shape", async () => {
    const result = await commands.getDiagnostics();
    expect(result).toHaveProperty("runtime");
    expect(result).toHaveProperty("gateway");
    expect(result).toHaveProperty("sync");
    expect(result).toHaveProperty("resources");
    expect(result).toHaveProperty("errors");
    expect(result.runtime).toHaveProperty("status");
    expect(result.runtime).toHaveProperty("pid");
    expect(result.gateway).toHaveProperty("status");
    expect(result.gateway).toHaveProperty("latency");
    expect(result.sync).toHaveProperty("status");
    expect(result.resources).toHaveProperty("memory");
    expect(Array.isArray(result.errors)).toBe(true);
  });

  it("getCommands returns array of DesktopCommand", async () => {
    const result = await commands.getCommands();
    expect(Array.isArray(result)).toBe(true);
    for (const cmd of result) {
      expect(cmd).toHaveProperty("id");
      expect(cmd).toHaveProperty("title");
      expect(cmd).toHaveProperty("description");
      expect(cmd).toHaveProperty("category");
      expect(cmd).toHaveProperty("icon");
    }
  });

  it("getSettings returns expected shape", async () => {
    const result = await commands.getSettings();
    expect(result).toHaveProperty("appearance");
    expect(result).toHaveProperty("shortcuts");
    expect(result).toHaveProperty("notifications");
    expect(result).toHaveProperty("workspace");
    expect(result).toHaveProperty("offline");
    expect(result).toHaveProperty("general");
    expect(result.appearance).toHaveProperty("theme");
    expect(Array.isArray(result.shortcuts)).toBe(true);
  });

  it("getNotifications returns array", async () => {
    const result = await commands.getNotifications();
    expect(Array.isArray(result)).toBe(true);
    for (const n of result) {
      expect(n).toHaveProperty("id");
      expect(n).toHaveProperty("type");
      expect(n).toHaveProperty("title");
      expect(n).toHaveProperty("message");
      expect(n).toHaveProperty("severity");
      expect(n).toHaveProperty("timestamp");
      expect(n).toHaveProperty("read");
    }
  });

  it("getFileOperations returns array", async () => {
    const result = await commands.getFileOperations();
    expect(Array.isArray(result)).toBe(true);
    for (const f of result) {
      expect(f).toHaveProperty("id");
      expect(f).toHaveProperty("type");
      expect(f).toHaveProperty("path");
      expect(f).toHaveProperty("status");
      expect(f).toHaveProperty("size");
    }
  });

  it("getIntegrationContracts returns array", async () => {
    const result = await commands.getIntegrationContracts();
    expect(Array.isArray(result)).toBe(true);
    for (const c of result) {
      expect(c).toHaveProperty("id");
      expect(c).toHaveProperty("name");
      expect(c).toHaveProperty("application");
      expect(c).toHaveProperty("type");
      expect(c).toHaveProperty("available");
    }
  });

  it("getAuditEvents returns array", async () => {
    const result = await commands.getAuditEvents();
    expect(Array.isArray(result)).toBe(true);
    for (const e of result) {
      expect(e).toHaveProperty("id");
      expect(e).toHaveProperty("action");
      expect(e).toHaveProperty("module");
      expect(e).toHaveProperty("permission");
      expect(e).toHaveProperty("resource");
      expect(e).toHaveProperty("result");
      expect(e).toHaveProperty("timestamp");
    }
  });

  it("permissions commands return correct structure", async () => {
    const requestResult = await commands.requestPermission("file:read", "/test", "testing");
    expect(requestResult).toHaveProperty("id");
    expect(requestResult).toHaveProperty("status");

    const grantResult = await commands.grantPermission("test-id");
    expect(grantResult).toEqual({ success: true });

    const denyResult = await commands.denyPermission("test-id");
    expect(denyResult).toEqual({ success: true });

    const revokeResult = await commands.revokePermission("test-id");
    expect(revokeResult).toEqual({ success: true });
  });

  it("action commands return expected shapes", async () => {
    const sync = await commands.triggerSync();
    expect(sync).toEqual({ success: true });

    const offline = await commands.toggleOffline(true);
    expect(offline).toHaveProperty("enabled");

    const updates = await commands.checkUpdates();
    expect(updates).toHaveProperty("updateAvailable");
  });

  it("getCachedConversations returns array", async () => {
    const result = await commands.getCachedConversations();
    expect(Array.isArray(result)).toBe(true);
    for (const c of result) {
      expect(c).toHaveProperty("id");
      expect(c).toHaveProperty("title");
      expect(c).toHaveProperty("preview");
      expect(c).toHaveProperty("messageCount");
    }
  });

  it("getCachedKnowledge returns array", async () => {
    const result = await commands.getCachedKnowledge();
    expect(Array.isArray(result)).toBe(true);
    for (const k of result) {
      expect(k).toHaveProperty("id");
      expect(k).toHaveProperty("title");
      expect(k).toHaveProperty("summary");
      expect(k).toHaveProperty("collection");
    }
  });

  it("getQueuedActions returns array", async () => {
    const result = await commands.getQueuedActions();
    expect(Array.isArray(result)).toBe(true);
    for (const a of result) {
      expect(a).toHaveProperty("id");
      expect(a).toHaveProperty("type");
      expect(a).toHaveProperty("payload");
      expect(a).toHaveProperty("status");
    }
  });
});
