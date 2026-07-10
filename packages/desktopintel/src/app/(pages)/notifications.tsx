"use client";

import { motion } from "framer-motion";
import { Bell, CheckCheck, Trash2, Mail, MailOpen, Info, AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { formatRelativeTime } from "@/lib/utils";
import type { NotificationItem } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

const severityBorder: Record<string, string> = {
  error: "border-l-status-error",
  warning: "border-l-status-warning",
  success: "border-l-status-success",
  info: "border-l-status-info",
};

const severityIcon: Record<string, React.ReactNode> = {
  error: <AlertCircle className="h-4 w-4 text-status-error" />,
  warning: <AlertTriangle className="h-4 w-4 text-status-warning" />,
  success: <CheckCircle className="h-4 w-4 text-status-success" />,
  info: <Info className="h-4 w-4 text-status-info" />,
};

const typeBadge: Record<string, "default" | "secondary" | "destructive" | "warning" | "info"> = {
  workflow: "default",
  agent: "info",
  security: "destructive",
  automation: "warning",
  system: "secondary",
};

export function NotificationsPage() {
  const { notifications, markNotificationRead, clearNotifications } = useDesktopStore();

  const unread = notifications.filter((n) => !n.read);
  const read = notifications.filter((n) => n.read);

  const columns: Column<NotificationItem>[] = [
    {
      key: "type", header: "Type", render: (n) => (
        <Badge variant={typeBadge[n.type] || "secondary"} className="capitalize">{n.type}</Badge>
      ),
    },
    { key: "title", header: "Title", render: (n) => <span className="font-medium">{n.title}</span> },
    { key: "message", header: "Message", render: (n) => <span className="text-muted-foreground text-[11px]">{n.message}</span> },
    {
      key: "severity", header: "Severity", render: (n) => (
        <div className="flex items-center gap-1">
          {severityIcon[n.severity]}
          <span className="text-xs capitalize">{n.severity}</span>
        </div>
      ),
    },
    { key: "timestamp", header: "Timestamp", sortable: true, render: (n) => <span className="text-muted-foreground">{formatRelativeTime(n.timestamp)}</span> },
    {
      key: "read", header: "Read", render: (n) => n.read
        ? <MailOpen className="h-3.5 w-3.5 text-muted-foreground" />
        : <Mail className="h-3.5 w-3.5 text-primary" />,
    },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="Notifications"
          description={`${unread.length} unread · ${notifications.length} total`}
          action={
            notifications.length > 0 && (
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={clearNotifications}>
                  <Trash2 className="h-3.5 w-3.5 mr-1" />
                  Clear All
                </Button>
              </div>
            )
          }
        />
      </motion.div>

      {unread.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">UNREAD</p>
          {unread.map((n) => (
            <Card
              key={n.id}
              className={`border-l-4 ${severityBorder[n.severity]} cursor-pointer`}
              onClick={() => markNotificationRead(n.id)}
            >
              <CardContent className="p-3 flex items-start gap-3">
                <div className="mt-0.5">{severityIcon[n.severity]}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Badge variant={typeBadge[n.type] || "secondary"} className="capitalize">{n.type}</Badge>
                    <span className="text-xs text-muted-foreground">{formatRelativeTime(n.timestamp)}</span>
                  </div>
                  <p className="text-sm font-medium mt-1">{n.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{n.message}</p>
                </div>
                <Button size="sm" variant="ghost" className="h-7 w-7 p-0 shrink-0">
                  <CheckCheck className="h-3.5 w-3.5" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </motion.div>
      )}

      <motion.div variants={itemVariants}>
        {notifications.length === 0 ? (
          <EmptyState
            icon={Bell}
            title="No notifications"
            description="Notifications from JARVIS will appear here"
          />
        ) : (
          <DataTable columns={columns} data={notifications} keyField="id" />
        )}
      </motion.div>
    </motion.div>
  );
}
