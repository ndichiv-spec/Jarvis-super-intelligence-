"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/shared/empty-state";
import { Bell, CheckCheck, Info, AlertTriangle, AlertCircle, CheckCircle2, Clock } from "lucide-react";
import { formatRelativeTime, cn } from "@/lib/utils";
import { motion } from "framer-motion";

const notifications = [
  { id: "1", type: "workflow" as const, title: "Backup Completed", message: "Daily backup workflow completed successfully", severity: "success" as const, read: false, timestamp: new Date(Date.now() - 600000) },
  { id: "2", type: "agent" as const, title: "Agent Task Complete", message: "CodeAssistant finished reviewing PR #142", severity: "info" as const, read: false, timestamp: new Date(Date.now() - 1800000) },
  { id: "3", type: "platform" as const, title: "Extension Update Available", message: "Tool Pack v1.0.0 is now available for update", severity: "warning" as const, read: false, timestamp: new Date(Date.now() - 3600000) },
  { id: "4", type: "security" as const, title: "New Device Login", message: "New login detected from Chrome on Windows", severity: "warning" as const, read: true, timestamp: new Date(Date.now() - 86400000) },
  { id: "5", type: "user" as const, title: "Memory Archived", message: "Low-confidence memories were automatically archived", severity: "info" as const, read: true, timestamp: new Date(Date.now() - 172800000) },
  { id: "6", type: "workflow" as const, title: "Price Monitor Failed", message: "Price monitoring workflow encountered an error", severity: "error" as const, read: true, timestamp: new Date(Date.now() - 259200000) },
  { id: "7", type: "platform" as const, title: "System Update", message: "Platform was updated to v11.2.0", severity: "success" as const, read: true, timestamp: new Date(Date.now() - 604800000) },
];

const typeIcons = {
  workflow: CheckCircle2,
  agent: Bell,
  security: AlertTriangle,
  platform: Info,
  user: Bell,
};

const severityColors = {
  info: "border-l-status-info",
  success: "border-l-status-success",
  warning: "border-l-status-warning",
  error: "border-l-status-error",
};

const severityBadge = {
  info: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  success: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  error: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function NotificationsPage() {
  const [tab, setTab] = useState("all");
  const [readState, setReadState] = useState<Record<string, boolean>>({});

  const toggleRead = (id: string) => {
    setReadState((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const markAllRead = () => {
    const all: Record<string, boolean> = {};
    notifications.forEach((n) => { all[n.id] = true; });
    setReadState(all);
  };

  const isRead = (id: string) => readState[id] !== undefined ? readState[id] : notifications.find((n) => n.id === id)?.read;

  const filtered = notifications.filter((n) => {
    if (tab === "unread") return !isRead(n.id);
    return true;
  });

  return (
    <div className="pb-8">
      <PageHeader
        title="Notifications"
        description="Stay informed about your ecosystem"
        actions={
          <Button variant="outline" size="sm" onClick={markAllRead}>
            <CheckCheck className="mr-2 h-4 w-4" />
            Mark All Read
          </Button>
        }
      />

      <div className="px-6 space-y-4">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="unread">Unread</TabsTrigger>
          </TabsList>

          <TabsContent value={tab} className="mt-4">
            {filtered.length === 0 ? (
              <EmptyState icon={Bell} title="All caught up!" description="No notifications to show" />
            ) : (
              <div className="space-y-2">
                {filtered.map((notif, i) => {
                  const Icon = typeIcons[notif.type] || Bell;
                  const read = isRead(notif.id);
                  return (
                    <motion.div
                      key={notif.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      <Card
                        className={cn(
                          "cursor-pointer border-l-4 transition-colors hover:bg-accent/50",
                          severityColors[notif.severity],
                          read ? "opacity-60" : "",
                        )}
                        onClick={() => toggleRead(notif.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <div className={cn("flex h-8 w-8 items-center justify-center rounded-full shrink-0", read ? "bg-muted" : "bg-primary/10")}>
                              <Icon className={cn("h-4 w-4", read ? "text-muted-foreground" : "text-primary")} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className={cn("text-sm font-medium", !read && "font-semibold")}>{notif.title}</span>
                                <Badge variant="secondary" className={cn("text-[10px]", severityBadge[notif.severity])}>{notif.severity}</Badge>
                                {!read && <span className="h-2 w-2 rounded-full bg-primary" />}
                              </div>
                              <p className="text-sm text-muted-foreground mt-0.5">{notif.message}</p>
                              <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                                <Clock className="h-3 w-3" />
                                {formatRelativeTime(notif.timestamp)}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
