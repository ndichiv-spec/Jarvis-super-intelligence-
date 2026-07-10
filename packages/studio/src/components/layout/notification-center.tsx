"use client";

import { Bell, CheckCheck, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface Notification {
  id: string;
  title: string;
  message: string;
  type: "success" | "warning" | "info" | "error";
  timestamp: string;
  read: boolean;
}

const defaultNotifications: Notification[] = [
  { id: "n1", title: "Workflow completed", message: "Data pipeline finished successfully", type: "success", timestamp: "2m ago", read: false },
  { id: "n2", title: "Agent idle", message: "CodingAgent has been idle for 5m", type: "warning", timestamp: "5m ago", read: false },
  { id: "n3", title: "Memory consolidated", message: "3 memory items archived", type: "info", timestamp: "15m ago", read: false },
  { id: "n4", title: "Error threshold exceeded", message: "VisionAgent error rate > 5%", type: "error", timestamp: "1h ago", read: true },
  { id: "n5", title: "Deployment queued", message: "Production deployment queued for review", type: "info", timestamp: "2h ago", read: true },
];

const typeStyles: Record<string, string> = {
  success: "bg-green-500/10 text-green-500 border-green-500/20",
  warning: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  info: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  error: "bg-red-500/10 text-red-500 border-red-500/20",
};

export function NotificationCenter() {
  const [notifications, setNotifications] = useState(defaultNotifications);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative h-8 w-8">
          <Bell className="h-3.5 w-3.5" />
          {unreadCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-red-500 text-[8px] font-medium text-white">
              {unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80" align="end">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Notifications</span>
          <div className="flex gap-1">
            {unreadCount > 0 && (
              <button onClick={markAllRead} className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground">
                <CheckCheck className="h-3 w-3" /> Mark all read
              </button>
            )}
            {notifications.length > 0 && (
              <button onClick={clearAll} className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground ml-2">
                <X className="h-3 w-3" /> Clear
              </button>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="max-h-72 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="py-6 text-center text-sm text-muted-foreground">No notifications</div>
          ) : (
            notifications.map((n) => (
              <div key={n.id} className={cn("flex gap-3 border-b px-3 py-2.5 last:border-0", !n.read && "bg-accent/30")}>
                <div className={cn("mt-0.5 h-2 w-2 shrink-0 rounded-full", n.type === "success" ? "bg-green-500" : n.type === "warning" ? "bg-yellow-500" : n.type === "error" ? "bg-red-500" : "bg-blue-500")} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium">{n.title}</p>
                  <p className="text-[10px] text-muted-foreground truncate">{n.message}</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">{n.timestamp}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
