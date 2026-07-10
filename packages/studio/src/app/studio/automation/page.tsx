"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable, type Column } from "@/components/shared/data-table";
import { StatusDot } from "@/components/shared/status-dot";
import { MetricChart } from "@/components/shared/metric-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  PlayCircle, History, BarChart3, AlertTriangle, Clock,
} from "lucide-react";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

interface RunningWorkflow {
  id: string;
  name: string;
  startedAt: string;
  duration: string;
  status: string;
  progress: number;
}

interface HistoryExecution {
  id: string;
  name: string;
  status: "completed" | "failed";
  startedAt: string;
  completedAt: string;
  duration: string;
  trigger: string;
}

interface FailedExecution {
  id: string;
  name: string;
  errorMessage: string;
  failedAt: string;
  duration: string;
}

const runningWorkflows: RunningWorkflow[] = [
  { id: "rw1", name: "Data Pipeline", startedAt: "10:32 AM", duration: "4m 12s", status: "running", progress: 62 },
  { id: "rw2", name: "Report Generator", startedAt: "10:45 AM", duration: "2m 08s", status: "running", progress: 34 },
  { id: "rw3", name: "Alert Processor", startedAt: "10:50 AM", duration: "1m 45s", status: "running", progress: 87 },
  { id: "rw4", name: "Sync Engine", startedAt: "10:55 AM", duration: "0m 32s", status: "running", progress: 15 },
];

const historyExecutions: HistoryExecution[] = [
  { id: "he1", name: "Data Pipeline", status: "completed", startedAt: "9:15 AM", completedAt: "9:19 AM", duration: "4m 12s", trigger: "scheduled" },
  { id: "he2", name: "Backup Scheduler", status: "completed", startedAt: "8:00 AM", completedAt: "8:05 AM", duration: "5m 00s", trigger: "scheduled" },
  { id: "he3", name: "Report Generator", status: "failed", startedAt: "7:30 AM", completedAt: "7:32 AM", duration: "2m 34s", trigger: "manual" },
  { id: "he4", name: "Alert Processor", status: "completed", startedAt: "7:00 AM", completedAt: "7:01 AM", duration: "1m 08s", trigger: "event" },
  { id: "he5", name: "Data Pipeline", status: "completed", startedAt: "6:00 AM", completedAt: "6:04 AM", duration: "4m 12s", trigger: "scheduled" },
  { id: "he6", name: "Sync Engine", status: "completed", startedAt: "5:30 AM", completedAt: "5:36 AM", duration: "6m 21s", trigger: "scheduled" },
  { id: "he7", name: "Backup Scheduler", status: "failed", startedAt: "4:00 AM", completedAt: "4:01 AM", duration: "1m 45s", trigger: "scheduled" },
  { id: "he8", name: "Alert Processor", status: "completed", startedAt: "3:00 AM", completedAt: "3:01 AM", duration: "1m 08s", trigger: "event" },
];

const failedExecutions: FailedExecution[] = [
  { id: "fe1", name: "Report Generator", errorMessage: "Timeout exceeded after 30s", failedAt: "7:32 AM", duration: "2m 34s" },
  { id: "fe2", name: "Backup Scheduler", errorMessage: "Connection refused: database", failedAt: "4:01 AM", duration: "1m 45s" },
  { id: "fe3", name: "Data Pipeline", errorMessage: "Out of memory in node 4", failedAt: "1:15 AM", duration: "3m 22s" },
];

const executionTimeData = [
  { label: "Mon", value: 24 },
  { label: "Tue", value: 18 },
  { label: "Wed", value: 32 },
  { label: "Thu", value: 27 },
  { label: "Fri", value: 15 },
  { label: "Sat", value: 8 },
  { label: "Sun", value: 12 },
];

const triggerVariant: Record<string, "default" | "secondary" | "outline" | "success" | "warning" | "info"> = {
  scheduled: "default",
  manual: "secondary",
  event: "info",
};

const runningColumns: Column<RunningWorkflow>[] = [
  {
    key: "name",
    header: "Workflow",
    cell: (w) => <span className="font-medium">{w.name}</span>,
  },
  {
    key: "startedAt",
    header: "Started",
    cell: (w) => <span className="text-muted-foreground">{w.startedAt}</span>,
  },
  {
    key: "duration",
    header: "Duration",
    cell: (w) => <span className="text-muted-foreground">{w.duration}</span>,
  },
  {
    key: "status",
    header: "Status",
    cell: (w) => (
      <div className="flex items-center gap-2">
        <StatusDot status="running" />
        <div className="flex flex-col gap-1 min-w-[100px]">
          <span className="text-xs capitalize text-muted-foreground">Running</span>
          <Progress value={w.progress} className="h-1.5" />
        </div>
      </div>
    ),
  },
];

const historyColumns: Column<HistoryExecution>[] = [
  {
    key: "name",
    header: "Workflow",
    cell: (e) => <span className="font-medium">{e.name}</span>,
  },
  {
    key: "status",
    header: "Status",
    cell: (e) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={e.status === "completed" ? "success" : "error"} />
        <span className="text-xs capitalize">{e.status}</span>
      </div>
    ),
  },
  {
    key: "startedAt",
    header: "Started",
    cell: (e) => <span className="text-muted-foreground">{e.startedAt}</span>,
  },
  {
    key: "completedAt",
    header: "Completed",
    cell: (e) => <span className="text-muted-foreground">{e.completedAt}</span>,
  },
  {
    key: "duration",
    header: "Duration",
    cell: (e) => <span className="text-muted-foreground">{e.duration}</span>,
  },
  {
    key: "trigger",
    header: "Trigger",
    cell: (e) => (
      <Badge variant={triggerVariant[e.trigger] || "outline"} className="text-xs">
        {e.trigger}
      </Badge>
    ),
  },
];

const failedColumns: Column<FailedExecution>[] = [
  {
    key: "name",
    header: "Workflow",
    cell: (f) => <span className="font-medium">{f.name}</span>,
  },
  {
    key: "error",
    header: "Error",
    cell: (f) => (
      <span className="text-xs text-destructive max-w-[240px] truncate block" title={f.errorMessage}>
        {f.errorMessage}
      </span>
    ),
  },
  {
    key: "failedAt",
    header: "Failed At",
    cell: (f) => <span className="text-muted-foreground">{f.failedAt}</span>,
  },
  {
    key: "duration",
    header: "Duration",
    cell: (f) => <span className="text-muted-foreground">{f.duration}</span>,
  },
  {
    key: "status",
    header: "Status",
    cell: () => (
      <Badge variant="destructive" className="text-xs">
        Failed
      </Badge>
    ),
  },
];

export default function AutomationPage() {
  const { data: workflowsData } = useData(() => api.workflows.list());
  const { data: executionsData } = useData(() => api.workflows.executions(""));
  const running = runningWorkflows.length;
  const completedToday = historyExecutions.filter((e) => e.status === "completed").length;
  const failed = historyExecutions.filter((e) => e.status === "failed").length + failedExecutions.length;
  const avgDuration = "2m 51s";

  return (
    <div className="pb-8">
      <PageHeader
        title="Automation Monitor"
        description="Observe automation in real time"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Running" value={running} icon={PlayCircle} />
          <StatCard title="Completed Today" value={completedToday} icon={History} trend={{ value: 12, positive: true }} />
          <StatCard title="Failed" value={failed} icon={AlertTriangle} trend={{ value: 8, positive: false }} />
          <StatCard title="Avg Duration" value={avgDuration} icon={Clock} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="running">
            <TabsList>
              <TabsTrigger value="running">
                <PlayCircle className="h-3.5 w-3.5 mr-1.5" />
                Running Workflows
              </TabsTrigger>
              <TabsTrigger value="history">
                <History className="h-3.5 w-3.5 mr-1.5" />
                History
              </TabsTrigger>
              <TabsTrigger value="performance">
                <BarChart3 className="h-3.5 w-3.5 mr-1.5" />
                Performance
              </TabsTrigger>
              <TabsTrigger value="failures">
                <AlertTriangle className="h-3.5 w-3.5 mr-1.5" />
                Failures
              </TabsTrigger>
            </TabsList>

            <TabsContent value="running" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Running Workflows</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable columns={runningColumns} data={runningWorkflows} emptyMessage="No workflows currently running" />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Execution History</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable columns={historyColumns} data={historyExecutions} emptyMessage="No historical executions found" />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="performance" className="mt-4">
              <div className="grid gap-4 lg:grid-cols-3">
                <div className="lg:col-span-2">
                  <MetricChart title="Execution Times" data={executionTimeData} />
                </div>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium">Average Duration</CardTitle>
                  </CardHeader>
                  <CardContent className="flex flex-col items-center justify-center py-8">
                    <Clock className="h-8 w-8 text-primary mb-3" />
                    <p className="text-3xl font-semibold">{avgDuration}</p>
                    <p className="text-xs text-muted-foreground mt-1">across all workflows</p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="failures" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Failed Executions</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable columns={failedColumns} data={failedExecutions} emptyMessage="No failures recorded" />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}
