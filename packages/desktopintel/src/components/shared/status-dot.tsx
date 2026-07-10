import { cn } from "@/lib/utils";

interface StatusDotProps {
  status: "healthy" | "degraded" | "error" | "connected" | "disconnected" | "synced" | "syncing" | "pending" | "offline" | "active" | "inactive" | "enabled" | "disabled";
  className?: string;
}

const statusColors: Record<string, string> = {
  healthy: "bg-status-success",
  connected: "bg-status-success",
  synced: "bg-status-success",
  active: "bg-status-success",
  enabled: "bg-status-success",
  degraded: "bg-status-warning",
  syncing: "bg-status-warning",
  pending: "bg-status-warning",
  error: "bg-status-error",
  disconnected: "bg-status-error",
  offline: "bg-status-error",
  inactive: "bg-status-pending",
  disabled: "bg-status-pending",
};

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span
      className={cn(
        "inline-block h-2 w-2 rounded-full",
        statusColors[status] || "bg-status-pending",
        className,
      )}
      aria-label={`Status: ${status}`}
    />
  );
}
