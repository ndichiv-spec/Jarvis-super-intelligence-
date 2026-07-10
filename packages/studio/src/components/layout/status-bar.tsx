"use client";

import { useAppStore } from "@/stores/app-store";
import { cn } from "@/lib/utils";
import { Activity, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";

export function StatusBar() {
  const { currentWorkspace, stats } = useAppStore();
  const [connected, setConnected] = useState(true);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 30000);
    return () => clearInterval(interval);
  }, []);

  const healthColor = {
    healthy: "text-green-500",
    degraded: "text-yellow-500",
    critical: "text-red-500",
  };

  return (
    <footer className="flex h-5 items-center justify-between border-t bg-sidebar px-3 text-[10px] text-muted-foreground">
      <div className="flex items-center gap-3">
        {connected ? (
          <span className="flex items-center gap-1">
            <Wifi className="h-2.5 w-2.5 text-green-500" />
            Connected
          </span>
        ) : (
          <span className="flex items-center gap-1">
            <WifiOff className="h-2.5 w-2.5 text-red-500" />
            Disconnected
          </span>
        )}
        {currentWorkspace && (
          <>
            <span className="text-[10px]">|</span>
            <span>WS: {currentWorkspace.name}</span>
            <span className={cn("text-[10px]", currentWorkspace.environment === "production" ? "text-orange-500" : "text-blue-400")}>
              {currentWorkspace.environment}
            </span>
          </>
        )}
      </div>

      <div className="flex items-center gap-3">
        {stats && (
          <span className={cn("flex items-center gap-1", healthColor[stats.platformHealth])}>
            <Activity className="h-2.5 w-2.5" />
            {stats.platformHealth}
          </span>
        )}
        <span>{time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
      </div>
    </footer>
  );
}
