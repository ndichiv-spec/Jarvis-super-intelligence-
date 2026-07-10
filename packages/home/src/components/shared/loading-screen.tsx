"use client";

import type { StartupStage, StartupEvent } from "@/hooks/use-startup";

const stageLabels: Record<StartupStage, string> = {
  idle: "Starting...",
  config: "Initializing configuration...",
  gateway: "Connecting to Gateway...",
  health: "Checking platform health...",
  dashboard: "Loading dashboard...",
  ready: "Ready.",
  error: "Startup failed",
  timeout: "Startup timed out",
};

const stageOrder: StartupStage[] = ["config", "gateway", "health", "dashboard"];

interface LoadingScreenProps {
  stage: StartupStage;
  events: StartupEvent[];
}

export function LoadingScreen({ stage, events }: LoadingScreenProps) {
  const completedStages = events.filter((e) => e.status === "success").map((e) => e.stage);
  const currentIdx = stageOrder.indexOf(stage as (typeof stageOrder)[number]);

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="flex w-80 flex-col items-center gap-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
          <span className="text-lg font-bold text-primary-foreground">J</span>
        </div>

        <div className="w-full space-y-2">
          {stageOrder.map((s, i) => {
            const done = completedStages.includes(s);
            const active = stage === s;
            return (
              <div key={s} className="flex items-center gap-3 text-sm">
                <div
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-medium ${
                    done
                      ? "bg-green-500/20 text-green-600"
                      : active
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground"
                  }`}
                >
                  {done ? "✓" : active ? "●" : `${i + 1}`}
                </div>
                <span
                  className={
                    done
                      ? "text-green-600"
                      : active
                        ? "text-foreground font-medium"
                        : currentIdx > i
                          ? "text-muted-foreground/50"
                          : "text-muted-foreground"
                  }
                >
                  {stageLabels[s]}
                </span>
              </div>
            );
          })}
        </div>

        <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all duration-500"
            style={{ width: `${Math.min(((currentIdx + 1) / stageOrder.length) * 100, 100)}%` }}
          />
        </div>

        <p className="text-xs text-muted-foreground">{stageLabels[stage]}</p>
      </div>
    </div>
  );
}
