"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable, type Column } from "@/components/shared/data-table";
import { StatusDot } from "@/components/shared/status-dot";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GitBranch, PlayCircle, CheckCircle2, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

interface Workflow {
  id: string;
  name: string;
  version: string;
  status: "draft" | "published" | "archived";
  nodeCount: number;
  updatedAt: string;
}

interface Execution {
  id: string;
  workflowId: string;
  status: "running" | "completed" | "failed";
  startedAt: string;
  duration: string;
  trigger: string;
}

const mockWorkflows: Workflow[] = [
  { id: "w1", name: "Data Pipeline", version: "v2.1", status: "published", nodeCount: 12, updatedAt: "2h ago" },
  { id: "w2", name: "Report Generator", version: "v1.4", status: "published", nodeCount: 8, updatedAt: "1d ago" },
  { id: "w3", name: "Backup Scheduler", version: "v3.0", status: "draft", nodeCount: 5, updatedAt: "3d ago" },
  { id: "w4", name: "Alert Processor", version: "v1.0", status: "published", nodeCount: 15, updatedAt: "5h ago" },
  { id: "w5", name: "Sync Engine", version: "v0.9", status: "archived", nodeCount: 7, updatedAt: "1w ago" },
];

const mockExecutions: Execution[] = [
  { id: "e1", workflowId: "Data Pipeline", status: "completed", startedAt: "10:32 AM", duration: "4m 12s", trigger: "scheduled" },
  { id: "e2", workflowId: "Report Generator", status: "running", startedAt: "10:45 AM", duration: "--", trigger: "manual" },
  { id: "e3", workflowId: "Alert Processor", status: "completed", startedAt: "9:15 AM", duration: "1m 8s", trigger: "event" },
  { id: "e4", workflowId: "Data Pipeline", status: "failed", startedAt: "8:00 AM", duration: "2m 34s", trigger: "scheduled" },
  { id: "e5", workflowId: "Sync Engine", status: "completed", startedAt: "7:30 AM", duration: "6m 21s", trigger: "scheduled" },
  { id: "e6", workflowId: "Backup Scheduler", status: "running", startedAt: "10:50 AM", duration: "--", trigger: "scheduled" },
];

const statusVariant: Record<string, "default" | "success" | "warning" | "info"> = {
  running: "info",
  completed: "success",
  failed: "warning",
};

const workflowColumns: Column<Workflow>[] = [
  {
    key: "name",
    header: "Name",
    cell: (w) => <span className="font-medium">{w.name}</span>,
  },
  {
    key: "version",
    header: "Version",
    cell: (w) => <Badge variant="outline" className="text-xs">{w.version}</Badge>,
  },
  {
    key: "status",
    header: "Status",
    cell: (w) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={w.status} />
        <span className="text-xs capitalize">{w.status}</span>
      </div>
    ),
  },
  {
    key: "nodeCount",
    header: "Nodes",
    cell: (w) => <span className="text-muted-foreground">{w.nodeCount}</span>,
  },
  {
    key: "updatedAt",
    header: "Updated",
    cell: (w) => <span className="text-muted-foreground">{w.updatedAt}</span>,
  },
];

const executionColumns: Column<Execution>[] = [
  {
    key: "workflowId",
    header: "Workflow",
    cell: (e) => <span className="font-medium">{e.workflowId}</span>,
  },
  {
    key: "status",
    header: "Status",
    cell: (e) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={(e.status === "completed" ? "success" : e.status) as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
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
    key: "duration",
    header: "Duration",
    cell: (e) => <span className="text-muted-foreground">{e.duration}</span>,
  },
  {
    key: "trigger",
    header: "Trigger",
    cell: (e) => <Badge variant="outline" className="text-xs">{e.trigger}</Badge>,
  },
];

export default function WorkflowsPage() {
  const { data: workflowsData, loading, error } = useData(() => api.workflows.list());
  const workflowList = (workflowsData || mockWorkflows) as Workflow[];
  const published = workflowList.filter((w) => w.status === "published").length;
  const running = mockExecutions.filter((e) => e.status === "running").length;
  const failed = mockExecutions.filter((e) => e.status === "failed").length;

  return (
    <div className="pb-8">
      <PageHeader
        title="Workflow Designer"
        description="Create, manage, and monitor automated workflows"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Workflows" value={workflowList.length} icon={GitBranch} />
          <StatCard title="Published" value={published} icon={CheckCircle2} trend={{ value: 60, positive: true }} />
          <StatCard title="Running Executions" value={running} icon={PlayCircle} />
          <StatCard title="Failed" value={failed} icon={AlertTriangle} trend={{ value: 17, positive: false }} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Workflows</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="definitions">
                <TabsList className="mb-4">
                  <TabsTrigger value="definitions">Definitions</TabsTrigger>
                  <TabsTrigger value="executions">Executions</TabsTrigger>
                  <TabsTrigger value="designer">Designer</TabsTrigger>
                </TabsList>

                <TabsContent value="definitions">
                  <DataTable columns={workflowColumns} data={workflowList} emptyMessage="No workflow definitions found" />
                </TabsContent>

                <TabsContent value="executions">
                  <DataTable columns={executionColumns} data={mockExecutions} emptyMessage="No executions found" />
                </TabsContent>

                <TabsContent value="designer">
                  <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mb-4">
                        <GitBranch className="h-8 w-8 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold mb-1">React Flow Designer</h3>
                      <p className="text-sm text-muted-foreground max-w-md">
                        Visual workflow designer with drag-and-drop support. Conditional branches, parallel execution, retry policies, approval nodes.
                      </p>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
