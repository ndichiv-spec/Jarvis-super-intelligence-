import { cn } from "@/lib/utils";

interface StatusDotProps {
  status: "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy";
  className?: string;
}

const statusColors: Record<string, string> = {
  healthy: "bg-status-success",
  active: "bg-status-success",
  success: "bg-status-success",
  running: "bg-status-info",
  degraded: "bg-status-warning",
  warning: "bg-status-warning",
  pending: "bg-status-pending",
  idle: "bg-status-pending",
  critical: "bg-status-error",
  error: "bg-status-error",
  inactive: "bg-muted-foreground",
  busy: "bg-status-warning",
};

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span
      className={cn(
        "inline-block h-2 w-2 rounded-full",
        statusColors[status] || "bg-muted-foreground",
        className,
      )}
    />
  );
}
