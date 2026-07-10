"use client";

import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { X, Bell, CheckCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatRelativeTime } from "@/lib/utils";

const severityColors: Record<string, string> = {
  info: "border-l-status-info",
  warning: "border-l-status-warning",
  error: "border-l-status-error",
  success: "border-l-status-success",
};

export function NotificationPanel() {
  const { notifications, markNotificationRead, clearNotifications } = useDesktopStore();
  const { setNotificationPanelOpen } = useUIStore();

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-end pt-10"
      onClick={() => setNotificationPanelOpen(false)}
    >
      <div className="absolute inset-0 bg-black/20" />
      <div
        className="relative w-80 h-full bg-background border-l border-border shadow-lg flex flex-col animate-slide-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-3 h-10 border-b border-border">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            <span className="text-sm font-medium">Notifications</span>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={clearNotifications}>
              <CheckCheck className="h-3.5 w-3.5" />
            </Button>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setNotificationPanelOpen(false)}>
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
        <ScrollArea className="flex-1">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bell className="h-8 w-8 text-muted-foreground/40 mb-2" />
              <p className="text-xs text-muted-foreground">No notifications</p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {notifications.map((n) => (
                <button
                  key={n.id}
                  className={cn(
                    "w-full text-left p-3 rounded-md border-l-2 transition-colors hover:bg-accent/50",
                    severityColors[n.severity] || "border-l-border",
                    n.read ? "opacity-60" : "",
                  )}
                  onClick={() => markNotificationRead(n.id)}
                >
                  <p className="text-xs font-medium">{n.title}</p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">{n.message}</p>
                  <p className="text-[10px] text-muted-foreground/60 mt-1">{formatRelativeTime(n.timestamp)}</p>
                </button>
              ))}
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  );
}
