"use client";

import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";
import { Button } from "@/components/ui/button";
import { StatusDot } from "@/components/shared/status-dot";
import {
  Bell,
  Search,
  Moon,
  Sun,
  Monitor,
} from "lucide-react";
import { useState, useEffect } from "react";

export function Titlebar() {
  const { state, settings, setTheme } = useDesktopStore();
  const { setNotificationPanelOpen, setCommandPaletteOpen } = useUIStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const unreadCount = 0; // TODO: from store
  const currentTheme = settings?.appearance?.theme || "system";

  const themeIcon = () => {
    if (!mounted) return <Monitor className="h-4 w-4" />;
    switch (currentTheme) {
      case "light": return <Sun className="h-4 w-4" />;
      case "dark": return <Moon className="h-4 w-4" />;
      default: return <Monitor className="h-4 w-4" />;
    }
  };

  const cycleTheme = () => {
    const themes: Array<"light" | "dark" | "system"> = ["light", "dark", "system"];
    const idx = themes.indexOf(currentTheme);
    setTheme(themes[(idx + 1) % themes.length]);
  };

  return (
    <header
      data-tauri-drag-region
      className="flex items-center justify-between h-10 px-3 border-b border-desktop-border bg-desktop-titlebar select-none"
    >
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5">
          <StatusDot status={state.runtime.gatewayConnected ? "connected" : "disconnected"} />
          <span className="text-xs text-muted-foreground">
            {state.runtime.gatewayConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
        <span className="text-xs text-muted-foreground/40 mx-1">|</span>
        <span className="text-xs font-mono text-muted-foreground">
          v{state.runtime.version}
        </span>
      </div>

      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setCommandPaletteOpen(true)}>
          <Search className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setNotificationPanelOpen(true)}>
          <div className="relative">
            <Bell className="h-3.5 w-3.5" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-destructive" />
            )}
          </div>
        </Button>
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={cycleTheme}>
          {themeIcon()}
        </Button>
      </div>
    </header>
  );
}
