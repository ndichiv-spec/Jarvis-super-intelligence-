"use client";

import { useState } from "react";
import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { MetricChart } from "@/components/shared/metric-chart";
import { DataTable } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  BarChart3, FileText, GitBranch, AlertTriangle, Activity,
  ChevronDown, ChevronRight,
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

const apiCallsData = [
  { label: "00:00", value: 120 },
  { label: "04:00", value: 85 },
  { label: "08:00", value: 240 },
  { label: "12:00", value: 310 },
  { label: "16:00", value: 275 },
  { label: "20:00", value: 190 },
];

const errorRateData = [
  { label: "00:00", value: 2.1 },
  { label: "04:00", value: 1.5 },
  { label: "08:00", value: 3.2 },
  { label: "12:00", value: 4.8 },
  { label: "16:00", value: 2.9 },
  { label: "20:00", value: 1.8 },
];

type LogLevel = "debug" | "info" | "warn" | "error";

interface LogEntry {
  id: string;
  level: LogLevel;
  source: string;
  message: string;
  timestamp: string;
}

interface Span {
  name: string;
  duration: string;
  status: string;
}

interface Trace {
  id: string;
  name: string;
  duration: string;
  status: string;
  spanCount: number;
  timestamp: string;
  spans: Span[];
}

type AlertSeverity = "critical" | "warning" | "info";

interface Alert {
  id: string;
  title: string;
  severity: AlertSeverity;
  source: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

const logEntries: LogEntry[] = [
  { id: "l1", level: "info", source: "api-gateway", message: "Request processed successfully", timestamp: "2026-06-30 14:32:01" },
  { id: "l2", level: "warn", source: "vector-store", message: "Query latency exceeded 500ms threshold", timestamp: "2026-06-30 14:28:45" },
  { id: "l3", level: "error", source: "agent-runtime", message: "Agent CodeAssistant crashed with OOM", timestamp: "2026-06-30 14:22:13" },
  { id: "l4", level: "info", source: "workflow-engine", message: "Workflow 'data-pipeline' completed in 3.2s", timestamp: "2026-06-30 14:18:09" },
  { id: "l5", level: "debug", source: "memory-cache", message: "Cache hit ratio: 0.87 for key pattern 'agent:*'", timestamp: "2026-06-30 14:15:22" },
  { id: "l6", level: "warn", source: "message-broker", message: "Consumer lag on topic 'events.agent' at 1200 messages", timestamp: "2026-06-30 14:10:55" },
  { id: "l7", level: "error", source: "security-scanner", message: "Vulnerability scan failed on endpoint /api/v2/agents", timestamp: "2026-06-30 14:05:33" },
  { id: "l8", level: "info", source: "api-gateway", message: "Rate limit applied to client 'external-webhook'", timestamp: "2026-06-30 14:00:00" },
];

const traces: Trace[] = [
  {
    id: "t1", name: "POST /api/v1/agents/execute", duration: "1.24s", status: "success", spanCount: 8,
    timestamp: "2026-06-30 14:32:01",
    spans: [
      { name: "HTTP POST", duration: "2ms", status: "success" },
      { name: "auth.verify", duration: "45ms", status: "success" },
      { name: "agent.invoke", duration: "890ms", status: "success" },
      { name: "llm.call", duration: "720ms", status: "success" },
      { name: "tool.exec", duration: "95ms", status: "success" },
    ],
  },
  {
    id: "t2", name: "GET /api/v1/workflows/status", duration: "340ms", status: "success", spanCount: 4,
    timestamp: "2026-06-30 14:28:45",
    spans: [
      { name: "HTTP GET", duration: "1ms", status: "success" },
      { name: "cache.lookup", duration: "12ms", status: "success" },
      { name: "db.query", duration: "280ms", status: "success" },
    ],
  },
  {
    id: "t3", name: "POST /api/v1/tools/search", duration: "2.81s", status: "error", spanCount: 6,
    timestamp: "2026-06-30 14:22:13",
    spans: [
      { name: "HTTP POST", duration: "3ms", status: "success" },
      { name: "auth.verify", duration: "38ms", status: "success" },
      { name: "search.execute", duration: "2.4s", status: "error" },
      { name: "vector.query", duration: "2.1s", status: "error" },
    ],
  },
  {
    id: "t4", name: "POST /api/v1/agents/stream", duration: "4.12s", status: "success", spanCount: 10,
    timestamp: "2026-06-30 14:18:09",
    spans: [
      { name: "HTTP POST", duration: "2ms", status: "success" },
      { name: "auth.verify", duration: "42ms", status: "success" },
      { name: "agent.stream", duration: "3.9s", status: "success" },
      { name: "llm.stream", duration: "3.5s", status: "success" },
      { name: "tool.exec", duration: "180ms", status: "success" },
    ],
  },
  {
    id: "t5", name: "DELETE /api/v1/knowledge/entries", duration: "680ms", status: "success", spanCount: 3,
    timestamp: "2026-06-30 14:10:55",
    spans: [
      { name: "HTTP DELETE", duration: "1ms", status: "success" },
      { name: "db.delete", duration: "620ms", status: "success" },
    ],
  },
];

const alerts: Alert[] = [
  { id: "a1", title: "High Memory Usage", severity: "critical", source: "agent-runtime", message: "Memory usage exceeded 90% on node-3 for 5 minutes", timestamp: "2026-06-30 14:30:00", acknowledged: false },
  { id: "a2", title: "API Latency Spike", severity: "warning", source: "api-gateway", message: "p95 latency spiked to 2.1s on /api/v1/agents/stream", timestamp: "2026-06-30 14:25:00", acknowledged: false },
  { id: "a3", title: "Certificate Expiring", severity: "warning", source: "security-scanner", message: "TLS certificate for *.jarvis.io expires in 7 days", timestamp: "2026-06-30 14:20:00", acknowledged: true },
  { id: "a4", title: "Vector Store Degraded", severity: "critical", source: "vector-store", message: "Qdrant cluster has 2 nodes unreachable", timestamp: "2026-06-30 14:15:00", acknowledged: false },
  { id: "a5", title: "Workflow Execution Failed", severity: "info", source: "workflow-engine", message: "Scheduled workflow 'nightly-backup' failed after 3 retries", timestamp: "2026-06-30 14:10:00", acknowledged: false },
  { id: "a6", title: "Rate Limit Threshold", severity: "info", source: "api-gateway", message: "Client 'webhook-prod' reached 80% of rate limit", timestamp: "2026-06-30 14:05:00", acknowledged: true },
];

const levelBadgeVariant: Record<LogLevel, "default" | "secondary" | "warning" | "destructive"> = {
  debug: "secondary",
  info: "default",
  warn: "warning",
  error: "destructive",
};

const severityBadgeVariant: Record<AlertSeverity, "destructive" | "warning" | "secondary"> = {
  critical: "destructive",
  warning: "warning",
  info: "secondary",
};

export default function ObservabilityPage() {
  const [expandedTraces, setExpandedTraces] = useState<Set<string>>(new Set());
  const { data: metricsData } = useData(() => api.observability.metrics());
  const { data: logsData } = useData(() => api.observability.logs());
  const { data: tracesData } = useData(() => api.observability.traces());
  const { data: alertsData } = useData(() => api.observability.alerts());
  const logEntriesList = (logsData || logEntries) as typeof logEntries;
  const tracesList = (tracesData || traces) as typeof traces;
  const alertsList = (alertsData || alerts) as typeof alerts;

  const toggleTrace = (id: string) => {
    setExpandedTraces((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div className="pb-8">
      <PageHeader
        title="Observability Center"
        description="Unified operational dashboard"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Metrics" value="1,284" icon={BarChart3} trend={{ value: 12, positive: true }} />
          <StatCard title="Logs Today" value="8,421" icon={FileText} />
          <StatCard title="Active Traces" value="156" icon={GitBranch} trend={{ value: 8, positive: true }} />
          <StatCard title="Active Alerts" value="3" icon={AlertTriangle} description="2 unacknowledged" />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="metrics">
            <TabsList>
              <TabsTrigger value="metrics">Metrics</TabsTrigger>
              <TabsTrigger value="logs">Logs</TabsTrigger>
              <TabsTrigger value="traces">Traces</TabsTrigger>
              <TabsTrigger value="alerts">Alerts</TabsTrigger>
            </TabsList>

            <TabsContent value="metrics" className="mt-4 space-y-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <MetricChart title="API Calls Over Time" data={apiCallsData} color="hsl(var(--primary))" />
                <MetricChart title="Error Rate (%)" data={errorRateData} color="hsl(var(--destructive))" />
              </div>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Activity className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Avg Response Time</p>
                      <p className="text-xl font-semibold">247ms</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <BarChart3 className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Total Requests</p>
                      <p className="text-xl font-semibold">24.5K</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <AlertTriangle className="h-5 w-5 text-destructive" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Error Count</p>
                      <p className="text-xl font-semibold">342</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Activity className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Uptime</p>
                      <p className="text-xl font-semibold">99.94%</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="logs" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Log Stream</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<LogEntry>
                    columns={[
                      {
                        key: "level",
                        header: "Level",
                        cell: (entry) => (
                          <Badge variant={levelBadgeVariant[entry.level]} className="text-[10px] uppercase">
                            {entry.level}
                          </Badge>
                        ),
                      },
                      {
                        key: "source",
                        header: "Source",
                        cell: (entry) => (
                          <span className="text-xs font-mono text-muted-foreground">{entry.source}</span>
                        ),
                      },
                      {
                        key: "message",
                        header: "Message",
                        cell: (entry) => (
                          <span className="text-xs">{entry.message}</span>
                        ),
                      },
                      {
                        key: "timestamp",
                        header: "Timestamp",
                        className: "text-right",
                        cell: (entry) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{entry.timestamp}</span>
                        ),
                      },
                    ]}
                    data={logEntriesList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="traces" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Trace Explorer</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-studio-border">
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider w-8" />
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Name</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Duration</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Spans</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-studio-border">
                      {tracesList.map((trace) => (
                        <tr key={trace.id} className="transition-colors hover:bg-studio-hover">
                          <td className="px-4 py-3 text-sm">
                            <button onClick={() => toggleTrace(trace.id)} className="p-0.5 hover:bg-accent rounded">
                              {expandedTraces.has(trace.id)
                                ? <ChevronDown className="h-3.5 w-3.5" />
                                : <ChevronRight className="h-3.5 w-3.5" />
                              }
                            </button>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <span className="font-mono text-xs">{trace.name}</span>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <span className="text-xs tabular-nums">{trace.duration}</span>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Badge
                              variant={trace.status === "success" ? "success" : "destructive"}
                              className="text-[10px]"
                            >
                              {trace.status}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-sm text-right">
                            <span className="text-xs tabular-nums">{trace.spanCount}</span>
                          </td>
                          <td className="px-4 py-3 text-sm text-right">
                            <span className="text-xs tabular-nums text-muted-foreground">{trace.timestamp}</span>
                          </td>
                        </tr>
                      ))}
                      {tracesList.map((trace) =>
                        expandedTraces.has(trace.id) && (
                          <tr key={`${trace.id}-spans`}>
                            <td colSpan={6} className="px-4 py-0">
                              <div className="bg-muted/30 border-t border-studio-border">
                                <table className="w-full">
                                  <thead>
                                    <tr className="border-b border-studio-border">
                                      <th className="px-10 py-2 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider w-8" />
                                      <th className="px-4 py-2 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Span Name</th>
                                      <th className="px-4 py-2 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Duration</th>
                                      <th className="px-4 py-2 text-left text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-studio-border">
                                    {trace.spans.map((span, idx) => (
                                      <tr key={idx} className="bg-muted/20">
                                        <td className="px-10 py-2 text-sm" />
                                        <td className="px-4 py-2 text-xs">{span.name}</td>
                                        <td className="px-4 py-2 text-xs tabular-nums">{span.duration}</td>
                                        <td className="px-4 py-2 text-xs">
                                          <Badge
                                            variant={span.status === "success" ? "success" : "destructive"}
                                            className="text-[10px]"
                                          >
                                            {span.status}
                                          </Badge>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="alerts" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Alert History</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<Alert>
                    columns={[
                      {
                        key: "title",
                        header: "Title",
                        cell: (alert) => (
                          <div className="flex items-center gap-2">
                            <AlertTriangle className={cn(
                              "h-3.5 w-3.5 shrink-0",
                              alert.severity === "critical" ? "text-destructive" :
                              alert.severity === "warning" ? "text-status-warning" : "text-muted-foreground",
                            )} />
                            <span className="font-medium">{alert.title}</span>
                          </div>
                        ),
                      },
                      {
                        key: "severity",
                        header: "Severity",
                        cell: (alert) => (
                          <Badge variant={severityBadgeVariant[alert.severity]} className="text-[10px] uppercase">
                            {alert.severity}
                          </Badge>
                        ),
                      },
                      {
                        key: "source",
                        header: "Source",
                        cell: (alert) => (
                          <span className="text-xs font-mono text-muted-foreground">{alert.source}</span>
                        ),
                      },
                      {
                        key: "message",
                        header: "Message",
                        cell: (alert) => (
                          <span className="text-xs text-muted-foreground max-w-[240px] truncate block">{alert.message}</span>
                        ),
                      },
                      {
                        key: "timestamp",
                        header: "Timestamp",
                        className: "text-right",
                        cell: (alert) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{alert.timestamp}</span>
                        ),
                      },
                      {
                        key: "acknowledged",
                        header: "Ack",
                        className: "text-center",
                        cell: (alert) => (
                          <Badge variant={alert.acknowledged ? "outline" : "secondary"} className="text-[10px]">
                            {alert.acknowledged ? "Acknowledged" : "Pending"}
                          </Badge>
                        ),
                      },
                    ]}
                    data={alertsList}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}

function cn(...classes: (string | false | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}
