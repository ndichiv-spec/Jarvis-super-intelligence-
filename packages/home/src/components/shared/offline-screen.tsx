"use client";

import type { StartupEvent } from "@/hooks/use-startup";
import { useState } from "react";

interface OfflineScreenProps {
  events: StartupEvent[];
  error: string | null;
  stage: string;
}

export function OfflineScreen({ events, error, stage }: OfflineScreenProps) {
  const [showLog, setShowLog] = useState(false);
  const isTimeout = stage === "timeout";

  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="flex h-screen items-center justify-center bg-background p-6">
      <div className="flex w-full max-w-md flex-col items-center gap-6 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-destructive/10">
          <span className="text-xl font-bold text-destructive">!</span>
        </div>

        <div className="space-y-2">
          <h1 className="text-lg font-semibold">
            {isTimeout ? "Startup Timeout" : "Connection Failed"}
          </h1>
          <p className="text-sm text-muted-foreground">
            {error || "The JARVIS Home application could not initialize."}
          </p>
        </div>

        {!isTimeout && (
          <p className="text-xs text-muted-foreground">
            Make sure the JARVIS backend is running on{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-[10px]">
              {process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000"}
            </code>
          </p>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleRetry}
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Retry
          </button>
          <button
            onClick={() => setShowLog(!showLog)}
            className="inline-flex h-9 items-center justify-center rounded-md border px-4 text-sm font-medium hover:bg-accent transition-colors"
          >
            {showLog ? "Hide Log" : "Diagnostics"}
          </button>
        </div>

        {showLog && (
          <div className="w-full rounded-lg border bg-muted/30 p-3 text-left">
            <p className="mb-2 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
              Startup Log
            </p>
            <div className="space-y-1">
              {events.map((e, i) => (
                <p
                  key={i}
                  className={`text-[10px] font-mono ${
                    e.status === "fail"
                      ? "text-destructive"
                      : e.status === "success"
                        ? "text-green-600"
                        : "text-muted-foreground"
                  }`}
                >
                  {`${new Date(e.timestamp).toLocaleTimeString()} [${e.stage}] ${e.message}`}
                  {e.error ? ` — ${e.error}` : ""}
                </p>
              ))}
            </div>
          </div>
        )}

        <p className="text-[10px] text-muted-foreground">
          JARVIS Home v1.0.0
        </p>
      </div>
    </div>
  );
}
