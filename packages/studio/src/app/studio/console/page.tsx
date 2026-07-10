"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import {
  Terminal, Bug, CheckCircle2, PlayCircle, Radio,
  AlertTriangle, Info, XCircle, Clock, Cpu, Wifi,
  HardDrive, Activity,
} from "lucide-react";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

type ConsoleLevel = "log" | "info" | "warn" | "error" | "debug";

interface ConsoleEntry {
  id: string;
  level: ConsoleLevel;
  message: string;
  source: string;
  timestamp: string;
}

const levelIcons: Record<ConsoleLevel, typeof Terminal> = {
  log: Terminal,
  info: Info,
  warn: AlertTriangle,
  error: XCircle,
  debug: Bug,
};

const levelBadgeVariant: Record<ConsoleLevel, "default" | "info" | "warning" | "destructive" | "secondary"> = {
  log: "default",
  info: "info",
  warn: "warning",
  error: "destructive",
  debug: "secondary",
};

const consoleEntries: ConsoleEntry[] = [
  { id: "c1", level: "info", message: "JARVIS Runtime initialized (v3.2.1)", source: "runtime", timestamp: "2026-06-30T14:32:01.123Z" },
  { id: "c2", level: "log", message: "Loading tool registry: 24 tools registered", source: "tool-manager", timestamp: "2026-06-30T14:32:00.456Z" },
  { id: "c3", level: "warn", message: "Redis connection retry #2 – backoff 1.5s", source: "cache", timestamp: "2026-06-30T14:31:58.789Z" },
  { id: "c4", level: "error", message: "Qdrant query failed: collection 'embeddings' not found", source: "vector-store", timestamp: "2026-06-30T14:31:55.321Z" },
  { id: "c5", level: "info", message: "Agent 'DataAnalyzer' deployed to worker pool", source: "agent-manager", timestamp: "2026-06-30T14:31:52.654Z" },
  { id: "c6", level: "debug", message: "WebSocket frame received: opcode=2, len=4096", source: "ws-server", timestamp: "2026-06-30T14:31:49.987Z" },
  { id: "c7", level: "log", message: "Workflow 'deploy-pipeline' execution started", source: "workflow-engine", timestamp: "2026-06-30T14:31:47.112Z" },
  { id: "c8", level: "warn", message: "API rate limit 85% exhausted for key sk-prod-*", source: "api-gateway", timestamp: "2026-06-30T14:31:44.445Z" },
  { id: "c9", level: "error", message: "SMTP connection refused: mail.internal:587", source: "email-service", timestamp: "2026-06-30T14:31:41.778Z" },
  { id: "c10", level: "info", message: "Extension 'slack-bridge' v2.1.0 activated", source: "extensions", timestamp: "2026-06-30T14:31:38.001Z" },
  { id: "c11", level: "debug", message: "GC pause: 42ms, freed 128MB heap", source: "jvm", timestamp: "2026-06-30T14:31:35.334Z" },
  { id: "c12", level: "log", message: "Health check passed – all 14 services online", source: "health-monitor", timestamp: "2026-06-30T14:31:32.667Z" },
];

interface Diagnostic {
  id: string;
  label: string;
  value: string;
  status: "healthy" | "degraded" | "down";
  icon: typeof Terminal;
}

const diagnostics: Diagnostic[] = [
  { id: "d1", label: "CPU Load", value: "23%", status: "healthy", icon: Cpu },
  { id: "d2", label: "Memory Usage", value: "1.4 GB / 4 GB", status: "healthy", icon: HardDrive },
  { id: "d3", label: "Network Latency", value: "12ms p95", status: "healthy", icon: Wifi },
  { id: "d4", label: "Database Pool", value: "8 / 20 connections", status: "healthy", icon: Activity },
  { id: "d5", label: "Message Queue", value: "1,234 pending", status: "degraded", icon: Radio },
  { id: "d6", label: "Disk I/O", value: "45 MB/s", status: "healthy", icon: HardDrive },
];

interface ValidationResult {
  id: string;
  rule: string;
  status: "pass" | "fail" | "warn";
  scope: string;
  message: string;
}

const validationResults: ValidationResult[] = [
  { id: "v1", rule: "schema-001", status: "pass", scope: "workflow/deploy-pipeline", message: "JSON Schema validation passed" },
  { id: "v2", rule: "perm-002", status: "pass", scope: "agent/DataAnalyzer", message: "All required permissions granted" },
  { id: "v3", rule: "conn-003", status: "fail", scope: "integration/slack-bridge", message: "Endpoint unreachable: https://slack.com/api" },
  { id: "v4", rule: "config-004", status: "warn", scope: "runtime/env", message: "LOG_LEVEL not set, defaulting to 'info'" },
  { id: "v5", rule: "dep-005", status: "pass", scope: "pipeline/build", message: "All dependencies resolved" },
  { id: "v6", rule: "sec-006", status: "fail", scope: "storage/secrets", message: "Expired TLS certificate for vault.internal" },
];

interface TaskEntry {
  id: string;
  task: string;
  status: "success" | "running" | "failed" | "pending";
  duration: string;
  started: string;
}

const taskEntries: TaskEntry[] = [
  { id: "t1", task: "deploy-pipeline", status: "success", duration: "12.3s", started: "2026-06-30T14:30:00Z" },
  { id: "t2", task: "index-embeddings", status: "running", duration: "—", started: "2026-06-30T14:31:00Z" },
  { id: "t3", task: "backup-databases", status: "success", duration: "45.1s", started: "2026-06-30T14:15:00Z" },
  { id: "t4", task: "security-scan", status: "failed", duration: "8.7s", started: "2026-06-30T14:00:00Z" },
  { id: "t5", task: "sync-knowledge-bases", status: "pending", duration: "—", started: "—" },
  { id: "t6", task: "health-check-all", status: "success", duration: "3.2s", started: "2026-06-30T13:45:00Z" },
];

interface PlatformEvent {
  id: string;
  type: string;
  source: string;
  severity: "info" | "warning" | "error";
  summary: string;
  timestamp: string;
}

const platformEvents: PlatformEvent[] = [
  { id: "e1", type: "MESSAGE_SENT", source: "orchestrator", severity: "info", summary: "Message dispatched to downstream handler", timestamp: "2026-06-30T14:32:01Z" },
  { id: "e2", type: "CONNECTION_ESTABLISHED", source: "websocket-server", severity: "info", summary: "New WebSocket connection from 10.0.1.42", timestamp: "2026-06-30T14:31:55Z" },
  { id: "e3", type: "ERROR", source: "redis-cache", severity: "error", summary: "Connection timeout after 5000ms", timestamp: "2026-06-30T14:31:52Z" },
  { id: "e4", type: "COMMAND_EXECUTED", source: "agent-manager", severity: "info", summary: "Command 'analyze' dispatched to DataAnalyzer", timestamp: "2026-06-30T14:31:48Z" },
  { id: "e5", type: "AUTH_FAILED", source: "api-gateway", severity: "warning", summary: "Invalid API key presented for endpoint /v1/events", timestamp: "2026-06-30T14:31:40Z" },
  { id: "e6", type: "HEARTBEAT", source: "message-broker", severity: "info", summary: "RabbitMQ node health check OK", timestamp: "2026-06-30T14:31:43Z" },
];

const validationColumns: Column<ValidationResult>[] = [
  { key: "rule", header: "Rule", cell: (v) => <code className="font-mono text-xs">{v.rule}</code> },
  {
    key: "status", header: "Status", cell: (v) => {
      const map = { pass: "success" as const, fail: "destructive" as const, warn: "warning" as const };
      return <Badge variant={map[v.status]} className="text-[10px]">{v.status}</Badge>;
    },
  },
  { key: "scope", header: "Scope", cell: (v) => <span className="font-mono text-xs text-muted-foreground">{v.scope}</span> },
  { key: "message", header: "Message", cell: (v) => <span className="text-xs">{v.message}</span> },
];

const taskColumns: Column<TaskEntry>[] = [
  { key: "task", header: "Task", cell: (t) => <span className="font-medium text-xs">{t.task}</span> },
  {
    key: "status", header: "Status", cell: (t) => {
      const iconMap = { success: CheckCircle2, running: PlayCircle, failed: XCircle, pending: Clock };
      const colorMap = { success: "text-status-success", running: "text-status-info", failed: "text-status-error", pending: "text-muted-foreground" };
      const Icon = iconMap[t.status];
      return (
        <div className="flex items-center gap-1.5">
          <Icon className={`h-3.5 w-3.5 ${colorMap[t.status]}`} />
          <span className={`text-xs ${colorMap[t.status]}`}>{t.status}</span>
        </div>
      );
    },
  },
  { key: "duration", header: "Duration", cell: (t) => <span className="font-mono text-xs text-muted-foreground">{t.duration}</span> },
  { key: "started", header: "Started", cell: (t) => <span className="text-xs text-muted-foreground">{t.started}</span> },
];

const eventColumns: Column<PlatformEvent>[] = [
  { key: "type", header: "Type", cell: (e) => <span className="text-xs font-medium">{e.type}</span> },
  { key: "source", header: "Source", cell: (e) => <span className="text-xs text-muted-foreground">{e.source}</span> },
  {
    key: "severity", header: "Severity", cell: (e) => {
      const map = { info: "info" as const, warning: "warning" as const, error: "destructive" as const };
      return <Badge variant={map[e.severity]} className="text-[10px]">{e.severity}</Badge>;
    },
  },
  { key: "summary", header: "Summary", cell: (e) => <span className="text-xs">{e.summary}</span> },
  {
    key: "timestamp", header: "Timestamp", cell: (e) => (
      <span className="text-xs tabular-nums text-muted-foreground">{new Date(e.timestamp).toLocaleTimeString()}</span>
    ),
  },
];

export default function DeveloperConsolePage() {
  const { data: logsData, loading, error } = useData(() => api.console.logs());
  const logEntriesList = (logsData || consoleEntries) as ConsoleEntry[];

  return (
    <div className="pb-8">
      <PageHeader
        title="Developer Console"
        description="Integrated engineering console for diagnostics, tasks, and platform events"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants}>
          <Tabs defaultValue="logs">
            <TabsList>
              <TabsTrigger value="logs" className="gap-1.5">
                <Terminal className="h-3.5 w-3.5" />
                Logs
              </TabsTrigger>
              <TabsTrigger value="diagnostics" className="gap-1.5">
                <Activity className="h-3.5 w-3.5" />
                Diagnostics
              </TabsTrigger>
              <TabsTrigger value="validation" className="gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Validation
              </TabsTrigger>
              <TabsTrigger value="tasks" className="gap-1.5">
                <PlayCircle className="h-3.5 w-3.5" />
                Tasks
              </TabsTrigger>
              <TabsTrigger value="events" className="gap-1.5">
                <Radio className="h-3.5 w-3.5" />
                Events
              </TabsTrigger>
            </TabsList>

            <TabsContent value="logs" className="mt-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between py-3">
                  <CardTitle className="text-sm font-medium">Console Output</CardTitle>
                  <Badge variant="outline" className="text-[10px] gap-1">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-success opacity-75" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-status-success" />
                    </span>
                    {logEntriesList.length} entries
                  </Badge>
                </CardHeader>
                <CardContent className="p-0">
                  <ScrollArea className="h-[420px]">
                    <div className="bg-[#0d1117] p-3 font-mono text-[13px] leading-relaxed space-y-0.5">
                      {logEntriesList.map((entry) => {
                        const Icon = levelIcons[entry.level];
                        return (
                          <div key={entry.id} className="flex items-start gap-2 py-0.5 px-1 rounded hover:bg-white/5 transition-colors">
                            <Icon className={`h-3.5 w-3.5 mt-0.5 shrink-0 ${
                              entry.level === "error" ? "text-status-error" :
                              entry.level === "warn" ? "text-status-warning" :
                              entry.level === "debug" ? "text-muted-foreground" :
                              "text-status-info"
                            }`} />
                            <Badge variant={levelBadgeVariant[entry.level]} className="text-[10px] px-1.5 py-0 shrink-0">
                              {entry.level}
                            </Badge>
                            <span className="flex-1 text-white/90">{entry.message}</span>
                            <span className="text-[11px] text-white/40 shrink-0 hidden sm:inline">{entry.source}</span>
                            <span className="text-[11px] text-white/30 shrink-0 hidden md:inline tabular-nums">
                              {new Date(entry.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="diagnostics" className="mt-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {diagnostics.map((d) => {
                  const statusColor =
                    d.status === "healthy" ? "text-status-success" :
                    d.status === "degraded" ? "text-status-warning" : "text-status-error";
                  const bgColor =
                    d.status === "healthy" ? "bg-status-success/10" :
                    d.status === "degraded" ? "bg-status-warning/10" : "bg-status-error/10";
                  return (
                    <Card key={d.id}>
                      <CardContent className="p-4 flex items-center gap-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${bgColor}`}>
                          <d.icon className={`h-5 w-5 ${statusColor}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-muted-foreground">{d.label}</p>
                          <p className="text-sm font-semibold">{d.value}</p>
                        </div>
                        <Badge variant={
                          d.status === "healthy" ? "success" :
                          d.status === "degraded" ? "warning" : "destructive"
                        } className="text-[10px]">
                          {d.status}
                        </Badge>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="validation" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Validation Results</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<ValidationResult>
                    columns={validationColumns}
                    data={validationResults}
                    emptyMessage="No validation results"
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tasks" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Task Execution</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<TaskEntry>
                    columns={taskColumns}
                    data={taskEntries}
                    emptyMessage="No task executions"
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="events" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Platform Events</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<PlatformEvent>
                    columns={eventColumns}
                    data={platformEvents}
                    emptyMessage="No platform events"
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardContent className="p-3">
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Enter a command..."
                  className="font-mono text-xs h-9"
                />
                <Button size="sm" className="gap-1.5 shrink-0">
                  <PlayCircle className="h-3.5 w-3.5" />
                  Execute
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
