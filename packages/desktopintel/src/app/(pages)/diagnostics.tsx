"use client";

import { motion } from "framer-motion";
import { Activity, Wifi, RefreshCw, MemoryStick, HardDrive, AlertTriangle, Bug } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatUptime, formatRelativeTime, formatBytes } from "@/lib/utils";
import type { DiagnosticsError } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function Diagnostics() {
  const { state } = useDesktopStore();
  const { diagnostics } = state;

  const memoryPercent = diagnostics.resources.memoryLimit > 0
    ? Math.round((diagnostics.resources.memory / diagnostics.resources.memoryLimit) * 100)
    : 0;
  const storagePercent = diagnostics.resources.storageLimit > 0
    ? Math.round((diagnostics.resources.storage / diagnostics.resources.storageLimit) * 100)
    : 0;

  const errorColumns: Column<DiagnosticsError>[] = [
    { key: "module", header: "Module", render: (e) => <Badge variant="outline">{e.module}</Badge> },
    { key: "message", header: "Message", render: (e) => <span className="text-muted-foreground">{e.message}</span> },
    {
      key: "severity", header: "Severity", render: (e) => (
        <Badge variant={e.severity === "error" ? "destructive" : "warning"}>{e.severity}</Badge>
      ),
    },
    { key: "timestamp", header: "Timestamp", sortable: true, render: (e) => <span className="text-muted-foreground">{formatRelativeTime(e.timestamp)}</span> },
    {
      key: "resolved", header: "Resolved", render: (e) => (
        <Badge variant={e.resolved ? "success" : "secondary"}>{e.resolved ? "Resolved" : "Open"}</Badge>
      ),
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
          title="Diagnostics"
          description="System health and performance monitoring"
        />
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-3 gap-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Runtime Health
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Status</span>
              <div className="flex items-center gap-1.5">
                <StatusDot status={diagnostics.runtime.status} />
                <span className="capitalize">{diagnostics.runtime.status}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">PID</span>
              <span className="font-mono">{diagnostics.runtime.pid}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Memory</span>
              <span>{formatBytes(diagnostics.runtime.memoryUsage)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">CPU</span>
              <span>{diagnostics.runtime.cpuUsage}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Uptime</span>
              <span>{formatUptime(diagnostics.runtime.uptime)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wifi className="h-4 w-4" />
              Gateway Connectivity
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Status</span>
              <div className="flex items-center gap-1.5">
                <StatusDot status={diagnostics.gateway.status === "connected" ? "connected" : diagnostics.gateway.status === "reconnecting" ? "pending" : "disconnected"} />
                <span className="capitalize">{diagnostics.gateway.status}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Latency</span>
              <span>{diagnostics.gateway.latency}ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Last Connected</span>
              <span>{diagnostics.gateway.lastConnected ? formatRelativeTime(diagnostics.gateway.lastConnected) : "Never"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Retry Count</span>
              <span>{diagnostics.gateway.retryCount}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Sync Health
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Status</span>
              <div className="flex items-center gap-1.5">
                <StatusDot status={diagnostics.sync.status} />
                <span className="capitalize">{diagnostics.sync.status}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Queue Depth</span>
              <span>{diagnostics.sync.queueDepth}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Failed Syncs</span>
              <span>{diagnostics.sync.failedSyncs}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Last Success</span>
              <span>{diagnostics.sync.lastSuccess ? formatRelativeTime(diagnostics.sync.lastSuccess) : "Never"}</span>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-2 gap-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MemoryStick className="h-4 w-4" />
              Memory Usage
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{formatBytes(diagnostics.resources.memory)}</span>
              <span className="text-muted-foreground">{formatBytes(diagnostics.resources.memoryLimit)}</span>
            </div>
            <Progress value={memoryPercent} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HardDrive className="h-4 w-4" />
              Storage Usage
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{formatBytes(diagnostics.resources.storage)}</span>
              <span className="text-muted-foreground">{formatBytes(diagnostics.resources.storageLimit)}</span>
            </div>
            <Progress value={storagePercent} />
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        {diagnostics.errors.length === 0 ? (
          <EmptyState
            icon={Bug}
            title="No errors"
            description="Diagnostic errors will appear here when issues are detected"
          />
        ) : (
          <>
            <SectionHeader title="Diagnostic Errors" description={`${diagnostics.errors.length} issues`} />
            <DataTable columns={errorColumns} data={diagnostics.errors} keyField="id" />
          </>
        )}
      </motion.div>
    </motion.div>
  );
}
