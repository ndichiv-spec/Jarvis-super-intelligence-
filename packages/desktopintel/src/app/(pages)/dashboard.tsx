"use client";

import { motion } from "framer-motion";
import { Clock, Activity, Layers, Cpu, Wifi, RefreshCw, Settings, Download, Zap } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { SectionHeader } from "@/components/shared/section-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatUptime, formatRelativeTime } from "@/lib/utils";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function Dashboard() {
  const { state, triggerSync, checkUpdates, setActivePage } = useDesktopStore();
  const { runtime, permissions, sync, updates } = state;

  const grantedCount = permissions.granted.filter((p) => !p.revoked).length;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="Dashboard"
          description="JARVIS Desktop Intelligence overview"
        />
      </motion.div>

      <motion.div variants={itemVariants} className="flex items-center gap-2 mb-2">
        <StatusDot status={runtime.gatewayConnected ? "connected" : "disconnected"} />
        <span className="text-xs font-medium">
          {runtime.gatewayConnected ? "Connected" : "Disconnected"}
        </span>
        <span className="text-xs text-muted-foreground">·</span>
        <span className="text-xs text-muted-foreground">v{runtime.version}</span>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-4 gap-3">
        <StatCard title="Version" value={`v${runtime.version}`} icon={Layers} />
        <StatCard title="Uptime" value={formatUptime(runtime.uptime)} icon={Clock} />
        <StatCard title="Session" value={runtime.sessionId.slice(0, 8)} icon={Activity} />
        <StatCard title="Capabilities" value={runtime.capabilities.length} icon={Cpu} />
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-3 gap-3">
        <StatCard
          title="Gateway Status"
          value={runtime.gatewayConnected ? "Connected" : "Disconnected"}
          icon={Wifi}
          trend={runtime.gatewayConnected ? { value: "Online", positive: true } : { value: "Offline", positive: false }}
        />
        <StatCard
          title="Sync State"
          value={sync.state.charAt(0).toUpperCase() + sync.state.slice(1)}
          icon={RefreshCw}
          trend={sync.state === "synced" ? { value: "Up to date", positive: true } : { value: `${sync.pendingChanges} pending`, positive: false }}
        />
        <StatCard
          title="Permissions Granted"
          value={grantedCount}
          icon={Zap}
          description={`${permissions.pending.length} pending requests`}
        />
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="p-4 space-y-3">
            <SectionHeader title="Runtime Information" />
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Version:</span>
                <Badge variant="default">{runtime.version}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Session:</span>
                <Badge variant="secondary">{runtime.sessionId.slice(0, 12)}...</Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Uptime:</span>
                <Badge variant="outline">{formatUptime(runtime.uptime)}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Started:</span>
                <Badge variant="outline">{formatRelativeTime(runtime.startedAt)}</Badge>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {runtime.capabilities.map((cap) => (
                <Badge key={cap} variant="info" className="text-[10px]">
                  {cap}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants} className="flex gap-2">
        <Button size="sm" onClick={triggerSync}>
          <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
          Sync Now
        </Button>
        <Button size="sm" variant="outline" onClick={checkUpdates}>
          <Download className="h-3.5 w-3.5 mr-1.5" />
          Check Updates
        </Button>
        <Button size="sm" variant="outline" onClick={() => setActivePage("settings")}>
          <Settings className="h-3.5 w-3.5 mr-1.5" />
          Open Settings
        </Button>
      </motion.div>
    </motion.div>
  );
}
