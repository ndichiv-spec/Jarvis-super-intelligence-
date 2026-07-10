"use client";

import { useDesktopStore } from "@/stores/desktop-store";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { SectionHeader } from "@/components/shared/section-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, AlertTriangle, Clock, Database } from "lucide-react";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
};

export function WorkspaceSync() {
  const { state, triggerSync } = useDesktopStore();
  const { sync } = state;

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-4">
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="Workspace Synchronization"
          description="Manage data synchronization across devices and workspaces"
          action={
            <Button size="sm" onClick={triggerSync}>
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Sync Now
            </Button>
          }
        />
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-4 gap-3">
        <StatCard title="Sync State" value={sync.state.charAt(0).toUpperCase() + sync.state.slice(1)} icon={RefreshCw}
          description={
            <span className="flex items-center gap-1.5 mt-1">
              <StatusDot status={sync.state as "synced" | "syncing" | "pending" | "offline"} />
              {sync.state}
            </span>
          }
        />
        <StatCard title="Pending Changes" value={sync.pendingChanges} icon={AlertTriangle} />
        <StatCard title="Conflicts" value={sync.conflicts} icon={AlertTriangle}
          trend={sync.conflicts > 0 ? { value: `${sync.conflicts} need resolution`, positive: false } : undefined}
        />
        <StatCard title="Last Sync" value={sync.lastSyncAt ? new Date(sync.lastSyncAt).toLocaleTimeString() : "Never"} icon={Clock} />
      </motion.div>

      <motion.div variants={itemVariants}>
        <SectionHeader title="Sync Modules" description="Individual sync module status" />
        <div className="grid grid-cols-2 gap-3">
          {sync.modules.map((mod) => (
            <Card key={mod.name}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <StatusDot status={mod.state as "synced" | "syncing" | "pending" | "error"} />
                      <span className="text-sm font-medium">{mod.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {mod.itemCount} items · Last sync: {mod.lastSyncAt ? new Date(mod.lastSyncAt).toLocaleTimeString() : "Never"}
                    </p>
                  </div>
                  <Badge variant={mod.state === "synced" ? "success" : mod.state === "error" ? "destructive" : "warning"}>
                    {mod.state}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </motion.div>

      {sync.conflicts > 0 && (
        <motion.div variants={itemVariants}>
          <Card className="border-status-warning">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-status-warning" />
                <span className="text-sm font-medium">Conflicts Detected</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {sync.conflicts} conflict(s) need manual resolution. Open the conflict resolver to review changes.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}
