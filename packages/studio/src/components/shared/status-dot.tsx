import { cn } from "@/lib/utils";

type StatusType = "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended";

interface StatusDotProps {
  status: StatusType;
  className?: string;
}

const statusColors: Record<string, string> = {
  healthy: "bg-status-success",
  active: "bg-status-success",
  success: "bg-status-success",
  available: "bg-status-success",
  running: "bg-status-info",
  degraded: "bg-status-warning",
  warning: "bg-status-warning",
  pending: "bg-status-pending",
  idle: "bg-status-pending",
  busy: "bg-status-warning",
  draft: "bg-status-pending",
  published: "bg-status-success",
  critical: "bg-status-error",
  error: "bg-status-error",
  inactive: "bg-muted-foreground",
  disabled: "bg-muted-foreground",
  suspended: "bg-status-error",
  maintenance: "bg-status-warning",
  archived: "bg-muted-foreground",
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
