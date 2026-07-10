"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatusDot } from "@/components/shared/status-dot";
import { EmptyState } from "@/components/shared/empty-state";
import {
  Zap,
  Plus,
  Play,
  Pause,
  RotateCcw,
  Clock,
  Timer,
  Activity,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import { motion } from "framer-motion";

const automations = [
  { id: "1", name: "Daily Backup", description: "Automated backup of all project data", status: "running" as const, type: "schedule" as const, lastRun: new Date(Date.now() - 1800000), nextRun: new Date(Date.now() + 21600000), executionCount: 342 },
  { id: "2", name: "Data Sync Pipeline", description: "Sync data between knowledge sources", status: "running" as const, type: "workflow" as const, lastRun: new Date(Date.now() - 600000), nextRun: new Date(Date.now() + 600000), executionCount: 128 },
  { id: "3", name: "Report Generation", description: "Generate weekly performance reports", status: "scheduled" as const, type: "schedule" as const, lastRun: new Date(Date.now() - 604800000), nextRun: new Date(Date.now() + 259200000), executionCount: 52 },
  { id: "4", name: "Memory Cleanup", description: "Archive low-confidence memories periodically", status: "completed" as const, type: "trigger" as const, lastRun: new Date(Date.now() - 7200000), executionCount: 89 },
  { id: "5", name: "Price Monitor", description: "Monitor competitor pricing changes", status: "failed" as const, type: "workflow" as const, lastRun: new Date(Date.now() - 3600000), executionCount: 15 },
  { id: "6", name: "Email Digest", description: "Compile and send daily activity digest", status: "paused" as const, type: "schedule" as const, lastRun: new Date(Date.now() - 1209600000), nextRun: undefined, executionCount: 44 },
];

const typeIcons = {
  workflow: Activity,
  trigger: Zap,
  schedule: Timer,
};

const statusColors: Record<string, string> = {
  running: "bg-status-success/10 text-status-success",
  scheduled: "bg-status-info/10 text-status-info",
  completed: "bg-muted text-muted-foreground",
  failed: "bg-status-error/10 text-status-error",
  paused: "bg-status-warning/10 text-status-warning",
};

export default function AutomationPage() {
  const [tab, setTab] = useState("all");

  const filtered = tab === "all" ? automations : automations.filter((a) => a.status === tab);

  return (
    <div className="pb-8">
      <PageHeader
        title="Automation Center"
        description="Manage your workflows and scheduled tasks"
        actions={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Automation
          </Button>
        }
      />

      <div className="px-6 space-y-4">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="running">Running</TabsTrigger>
            <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
            <TabsTrigger value="failed">Failed</TabsTrigger>
            <TabsTrigger value="paused">Paused</TabsTrigger>
          </TabsList>

          <TabsContent value={tab} className="mt-4">
            {filtered.length === 0 ? (
              <EmptyState icon={Zap} title="No automations found" description="Create your first automation to get started" />
            ) : (
              <div className="grid gap-3">
                {filtered.map((auto, i) => {
                  const TypeIcon = typeIcons[auto.type] || Activity;
                  return (
                    <motion.div
                      key={auto.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      <Card>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-4">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 shrink-0">
                              <TypeIcon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">{auto.name}</span>
                                <Badge variant="outline" className={statusColors[auto.status]}>
                                  <StatusDot status={auto.status === "running" ? "running" : auto.status === "scheduled" ? "pending" : auto.status === "failed" ? "error" : auto.status === "paused" ? "warning" : "success"} />
                                  <span className="ml-1 capitalize">{auto.status}</span>
                                </Badge>
                              </div>
                              <CardDescription className="text-xs mt-0.5">{auto.description}</CardDescription>
                              <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Activity className="h-3 w-3" />
                                  {auto.executionCount} executions
                                </span>
                                {auto.lastRun && (
                                  <span className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    Last: {formatRelativeTime(auto.lastRun)}
                                  </span>
                                )}
                                {auto.nextRun && (
                                  <span className="flex items-center gap-1">
                                    <Timer className="h-3 w-3" />
                                    Next: {formatRelativeTime(auto.nextRun)}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-1 shrink-0">
                              <Button variant="ghost" size="icon" className="h-8 w-8">
                                {auto.status === "running" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                              </Button>
                              <Button variant="ghost" size="icon" className="h-8 w-8">
                                <RotateCcw className="h-4 w-4" />
                              </Button>
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
