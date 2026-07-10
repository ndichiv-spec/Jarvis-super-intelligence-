"use client";

import { motion } from "framer-motion";
import { Wifi, WifiOff, MessageSquare, BookOpen, ListChecks, HardDrive, Globe } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { StatCard } from "@/components/shared/stat-card";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatRelativeTime, formatBytes } from "@/lib/utils";
import type { CachedConversation, CachedKnowledge, QueuedAction } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function OfflineMode() {
  const { state, cachedConversations, cachedKnowledge, queuedActions, toggleOffline } = useDesktopStore();
  const { offline } = state;

  const storagePercent = offline.storageLimit > 0
    ? Math.round((offline.storageUsed / offline.storageLimit) * 100)
    : 0;

  const conversationColumns: Column<CachedConversation>[] = [
    { key: "title", header: "Title", render: (c) => <span className="font-medium">{c.title}</span> },
    { key: "preview", header: "Preview", render: (c) => <span className="text-muted-foreground text-[11px]">{c.preview}</span> },
    { key: "messageCount", header: "Messages", render: (c) => <span className="text-muted-foreground">{c.messageCount}</span> },
    { key: "updatedAt", header: "Updated", sortable: true, render: (c) => <span className="text-muted-foreground">{formatRelativeTime(c.updatedAt)}</span> },
  ];

  const knowledgeColumns: Column<CachedKnowledge>[] = [
    { key: "title", header: "Title", render: (k) => <span className="font-medium">{k.title}</span> },
    { key: "summary", header: "Summary", render: (k) => <span className="text-muted-foreground text-[11px]">{k.summary}</span> },
    { key: "collection", header: "Collection", render: (k) => <Badge variant="secondary">{k.collection}</Badge> },
    { key: "cachedAt", header: "Cached", sortable: true, render: (k) => <span className="text-muted-foreground">{formatRelativeTime(k.cachedAt)}</span> },
  ];

  const actionColumns: Column<QueuedAction>[] = [
    { key: "type", header: "Type", render: (a) => <Badge variant="outline">{a.type}</Badge> },
    { key: "payload", header: "Payload", render: (a) => <span className="text-muted-foreground text-[11px] font-mono">{a.payload.slice(0, 40)}...</span> },
    { key: "queuedAt", header: "Queued", sortable: true, render: (a) => <span className="text-muted-foreground">{formatRelativeTime(a.queuedAt)}</span> },
    {
      key: "status", header: "Status", render: (a) => {
        const variant = a.status === "completed" ? "success" : a.status === "failed" ? "destructive" : a.status === "processing" ? "warning" : "secondary";
        return <Badge variant={variant}>{a.status}</Badge>;
      },
    },
    { key: "retryCount", header: "Retries", render: (a) => <span className="text-muted-foreground">{a.retryCount}</span> },
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
          title="Offline Mode"
          description="Manage offline capabilities and cached data"
        />
      </motion.div>

      <motion.div variants={itemVariants} className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Switch
            checked={offline.enabled}
            onCheckedChange={toggleOffline}
            id="offline-toggle"
          />
          <label htmlFor="offline-toggle" className="text-sm font-medium cursor-pointer">
            {offline.enabled ? "Offline Mode Enabled" : "Offline Mode Disabled"}
          </label>
        </div>
        {offline.enabled && (
          <Badge variant={offline.connected ? "success" : "secondary"}>
            {offline.connected ? "Connected" : "Disconnected"}
          </Badge>
        )}
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-4 gap-3">
        <StatCard title="Connected" value={offline.connected ? "Yes" : "No"} icon={offline.connected ? Wifi : WifiOff} />
        <StatCard title="Cached Conversations" value={offline.cachedConversations} icon={MessageSquare} />
        <StatCard title="Cached Knowledge" value={offline.cachedKnowledge} icon={BookOpen} />
        <StatCard title="Pending Actions" value={offline.pendingActions} icon={ListChecks} />
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="p-4 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Storage Usage</span>
              </div>
              <span className="text-xs text-muted-foreground">
                {formatBytes(offline.storageUsed)} / {formatBytes(offline.storageLimit)}
              </span>
            </div>
            <Progress value={storagePercent} />
          </CardContent>
        </Card>
      </motion.div>

      {cachedConversations.length > 0 && (
        <motion.div variants={itemVariants}>
          <SectionHeader title="Cached Conversations" description={`${cachedConversations.length} conversations`} />
          <DataTable columns={conversationColumns} data={cachedConversations} keyField="id" />
        </motion.div>
      )}

      {cachedKnowledge.length > 0 && (
        <motion.div variants={itemVariants}>
          <SectionHeader title="Cached Knowledge" description={`${cachedKnowledge.length} entries`} />
          <DataTable columns={knowledgeColumns} data={cachedKnowledge} keyField="id" />
        </motion.div>
      )}

      {queuedActions.length > 0 && (
        <motion.div variants={itemVariants}>
          <SectionHeader title="Queued Actions" description={`${queuedActions.length} actions pending`} />
          <DataTable columns={actionColumns} data={queuedActions} keyField="id" />
        </motion.div>
      )}

      {cachedConversations.length === 0 && cachedKnowledge.length === 0 && queuedActions.length === 0 && (
        <motion.div variants={itemVariants}>
          <EmptyState
            icon={Globe}
            title="No cached data"
            description="Cached conversations, knowledge, and queued actions will appear here when offline mode is active"
          />
        </motion.div>
      )}
    </motion.div>
  );
}
