"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useAppStore } from "@/stores/app-store";

export type StartupStage =
  | "idle"
  | "config"
  | "gateway"
  | "health"
  | "dashboard"
  | "ready"
  | "error"
  | "timeout";

export interface StartupEvent {
  stage: StartupStage;
  status: "start" | "success" | "fail";
  timestamp: number;
  message: string;
  error?: string;
}

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";
const STARTUP_TIMEOUT_MS = 10_000;

function now(): string {
  return new Date().toISOString().slice(11, 23);
}

async function checkConnectivity(url: string): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(url, { method: "GET", signal: controller.signal });
    clearTimeout(timeout);
    return res.ok;
  } catch {
    return false;
  }
}

export function useStartup() {
  const { setUser, setLoading } = useAppStore();
  const [stage, setStage] = useState<StartupStage>("idle");
  const [events, setEvents] = useState<StartupEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const startTime = useRef(Date.now());
  const timedOut = useRef(false);

  const log = useCallback(
    (s: StartupStage, status: StartupEvent["status"], message: string, err?: string) => {
      const event: StartupEvent = {
        stage: s,
        status,
        timestamp: Date.now(),
        message,
        error: err,
      };
      setEvents((prev) => [...prev, event]);
      console.log(`[Home] ${now()} ${status === "start" ? "→" : status === "success" ? "✓" : "✗"} ${message}`);
    },
    [],
  );

  const setStageAndLog = useCallback(
    (s: StartupStage, message: string) => {
      setStage(s);
      log(s, "start", message);
    },
    [log],
  );

  const succeedStage = useCallback(
    (s: StartupStage, message: string) => {
      log(s, "success", message);
    },
    [log],
  );

  const failStage = useCallback(
    (s: StartupStage, message: string, err: string) => {
      setStage("error");
      setError(err);
      log(s, "fail", message, err);
    },
    [log],
  );

  useEffect(() => {
    let cancelled = false;

    const timeout = setTimeout(() => {
      if (!cancelled && stage !== "ready" && stage !== "error") {
        timedOut.current = true;
        setStage("timeout");
        setError(`Startup timed out after ${STARTUP_TIMEOUT_MS / 1000}s`);
        log("timeout", "fail", `Startup exceeded ${STARTUP_TIMEOUT_MS / 1000}s limit`);
        setElapsed(Date.now() - startTime.current);
      }
    }, STARTUP_TIMEOUT_MS);

    async function start() {
      // Stage 1: Configuration
      if (cancelled) return;
      setStageAndLog("config", "Initializing configuration...");

      setUser({
        id: "user-1",
        name: "Alex Chen",
        email: "alex@example.com",
        role: "Developer",
        preferences: {
          theme: "system" as const,
          sidebarCollapsed: false,
          fontSize: "medium" as const,
          reducedMotion: false,
        },
      });
      succeedStage("config", "Configuration loaded");
      if (cancelled) return;

      // Stage 2: Gateway Connectivity
      setStageAndLog("gateway", "Connecting to Gateway...");
      const gatewayOk = await checkConnectivity(`${GATEWAY_URL}/`);
      if (cancelled) return;

      if (!gatewayOk) {
        const healthOk = await checkConnectivity(`${GATEWAY_URL}/health`);
        if (!healthOk) {
          failStage(
            "gateway",
            "Gateway connection failed",
            `Cannot reach ${GATEWAY_URL}. The JARVIS backend is not running.`,
          );
          return;
        }
      }
      succeedStage("gateway", "Gateway connected");
      if (cancelled) return;

      // Stage 3: Platform Health
      setStageAndLog("health", "Checking platform health...");
      try {
        const res = await fetch(`${GATEWAY_URL}/health`);
        if (res.ok) {
          succeedStage("health", "Platform healthy");
        } else {
          succeedStage("health", "Platform responded (degraded status)");
        }
      } catch {
        succeedStage("health", "Platform health check bypassed");
      }
      if (cancelled) return;

      // Stage 4: Dashboard stats
      setStageAndLog("dashboard", "Loading dashboard...");
      try {
        await fetch(`${GATEWAY_URL}/gateway/dashboard/stats`);
        succeedStage("dashboard", "Dashboard loaded");
      } catch {
        succeedStage("dashboard", "Dashboard offline (using local data)");
      }
      if (cancelled) return;

      // Done
      const total = Date.now() - startTime.current;
      setElapsed(total);
      log("ready", "success", `Startup completed in ${(total / 1000).toFixed(2)}s`);
      setStage("ready");

      // Unlock the UI
      setLoading(false);
    }

    start();

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { stage, events, error, elapsed };
}
