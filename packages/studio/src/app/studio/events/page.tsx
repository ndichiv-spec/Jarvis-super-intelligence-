"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable } from "@/components/shared/data-table";
import { StatusDot } from "@/components/shared/status-dot";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  Radio, Activity, AlertCircle, Search, GitBranch,
  BarChart3, Layers, Zap, Clock,
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

type EventSeverity = "info" | "warning" | "error" | "debug";

type EventType =
  | "MESSAGE_SENT"
  | "MESSAGE_RECEIVED"
  | "CONNECTION_ESTABLISHED"
  | "CONNECTION_CLOSED"
  | "ERROR"
  | "COMMAND_EXECUTED"
  | "AUTH_SUCCESS"
  | "AUTH_FAILED"
  | "SUBSCRIPTION_ACTIVATED"
  | "HEARTBEAT";

interface Event {
  id: string;
  type: EventType;
  source: string;
  correlationId: string;
  timestamp: string;
  severity: EventSeverity;
  summary: string;
}

const eventIcons: Record<string, typeof Radio> = {
  MESSAGE_SENT: Radio,
  MESSAGE_RECEIVED: Radio,
  CONNECTION_ESTABLISHED: GitBranch,
  CONNECTION_CLOSED: AlertCircle,
  ERROR: AlertCircle,
  COMMAND_EXECUTED: Search,
  AUTH_SUCCESS: Search,
  AUTH_FAILED: AlertCircle,
  SUBSCRIPTION_ACTIVATED: Activity,
  HEARTBEAT: Activity,
};

const severityBadgeVariant: Record<EventSeverity, "info" | "warning" | "destructive" | "secondary"> = {
  info: "info",
  warning: "warning",
  error: "destructive",
  debug: "secondary",
};

const severityDotStatus: Record<EventSeverity, "running" | "warning" | "error" | "idle"> = {
  info: "running",
  warning: "warning",
  error: "error",
  debug: "idle",
};

const MOCK_EVENTS: Event[] = [
  { id: "1", type: "MESSAGE_SENT", source: "orchestrator", correlationId: "corr-7a9f2b", timestamp: "2026-06-30T14:32:01.123Z", severity: "info", summary: "Message dispatched to downstream handler" },
  { id: "2", type: "MESSAGE_RECEIVED", source: "slack-bridge", correlationId: "corr-3c1d8e", timestamp: "2026-06-30T14:31:58.456Z", severity: "info", summary: "Incoming message from Slack channel #general" },
  { id: "3", type: "CONNECTION_ESTABLISHED", source: "websocket-server", correlationId: "corr-5e7a0f", timestamp: "2026-06-30T14:31:55.789Z", severity: "info", summary: "New WebSocket connection from 10.0.1.42" },
  { id: "4", type: "ERROR", source: "redis-cache", correlationId: "corr-9b2d4c", timestamp: "2026-06-30T14:31:52.321Z", severity: "error", summary: "Connection timeout after 5000ms" },
  { id: "5", type: "COMMAND_EXECUTED", source: "agent-manager", correlationId: "corr-1f8e3a", timestamp: "2026-06-30T14:31:48.654Z", severity: "info", summary: "Command 'analyze' dispatched to DataAnalyzer" },
  { id: "6", type: "AUTH_SUCCESS", source: "api-gateway", correlationId: "corr-6d2b9f", timestamp: "2026-06-30T14:31:45.987Z", severity: "info", summary: "Token validation passed for service-account-3" },
  { id: "7", type: "HEARTBEAT", source: "message-broker", correlationId: "corr-0a4c7e", timestamp: "2026-06-30T14:31:43.112Z", severity: "debug", summary: "RabbitMQ node health check OK" },
  { id: "8", type: "AUTH_FAILED", source: "api-gateway", correlationId: "corr-8f1d5b", timestamp: "2026-06-30T14:31:40.445Z", severity: "warning", summary: "Invalid API key presented for endpoint /v1/events" },
  { id: "9", type: "SUBSCRIPTION_ACTIVATED", source: "event-bus", correlationId: "corr-2e6c8a", timestamp: "2026-06-30T14:31:37.778Z", severity: "info", summary: "Topic 'workflow.completed' subscription registered" },
  { id: "10", type: "CONNECTION_CLOSED", source: "websocket-server", correlationId: "corr-4d9a1c", timestamp: "2026-06-30T14:31:35.001Z", severity: "warning", summary: "Client 10.0.1.42 disconnected: idle timeout" },
  { id: "11", type: "MESSAGE_RECEIVED", source: "mqtt-bridge", correlationId: "corr-7b3f0e", timestamp: "2026-06-30T14:31:32.334Z", severity: "info", summary: "MQTT message on topic sensors/temperature" },
  { id: "12", type: "COMMAND_EXECUTED", source: "workflow-engine", correlationId: "corr-5c2a8d", timestamp: "2026-06-30T14:31:29.667Z", severity: "info", summary: "Workflow 'deploy-pipeline' execution started" },
  { id: "13", type: "ERROR", source: "vector-store", correlationId: "corr-3f7b1e", timestamp: "2026-06-30T14:31:26.990Z", severity: "error", summary: "Qdrant collection 'embeddings' query failed: index not found" },
  { id: "14", type: "MESSAGE_SENT", source: "notification-service", correlationId: "corr-9e4d2a", timestamp: "2026-06-30T14:31:24.223Z", severity: "info", summary: "Push notification delivered to device token abc123" },
  { id: "15", type: "HEARTBEAT", source: "database-pool", correlationId: "corr-1a5c8f", timestamp: "2026-06-30T14:31:21.556Z", severity: "debug", summary: "PostgreSQL connection pool utilization at 34%" },
];

let errorCount: number, warningCount: number, infoCount: number, debugCount: number;

function EventCard({ event }: { event: Event }) {
  const Icon = eventIcons[event.type] || Radio;
  return (
    <div className="flex items-start gap-3 rounded-lg border p-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-medium">{event.type}</span>
          <Badge variant={severityBadgeVariant[event.severity]} className="text-[10px]">
            {event.severity}
          </Badge>
          <span className="text-[10px] text-muted-foreground">{event.source}</span>
        </div>
        <p className="text-xs text-muted-foreground">{event.summary}</p>
        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
          <code className="font-mono text-[10px] text-status-info">{event.correlationId}</code>
          <span>&middot;</span>
          <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}

export default function EventMonitorPage() {
  const { data: eventsData, loading, error } = useData(() => api.events.search({}));
  const events: Event[] = (eventsData as unknown as Event[]) || MOCK_EVENTS;
  const eventTypeCounts = events.reduce<Record<string, number>>((acc, e) => {
    acc[e.type] = (acc[e.type] || 0) + 1;
    return acc;
  }, {});
  const topEventTypes = Object.entries(eventTypeCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  errorCount = events.filter((e) => e.severity === "error").length;
  warningCount = events.filter((e) => e.severity === "warning").length;
  infoCount = events.filter((e) => e.severity === "info").length;
  debugCount = events.filter((e) => e.severity === "debug").length;

  return (
    <div className="pb-8">
      <PageHeader
        title="Event Monitor"
        description="Live event stream from the Communication Platform"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Events Today" value={events.length} icon={Radio} trend={{ value: 12, positive: true }} />
          <StatCard
            title="Error Rate"
            value={events.length > 0 ? `${((errorCount / events.length) * 100).toFixed(0)}%` : "0%"}
            icon={AlertCircle}
            trend={{ value: 2, positive: false }}
          />
          <StatCard title="Active Correlations" value="7" icon={GitBranch} description="Across 4 services" />
          <StatCard title="Avg Processing Time" value="24ms" icon={Clock} trend={{ value: 5, positive: true }} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="live">
            <TabsList>
              <TabsTrigger value="live" className="gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-success opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-status-success" />
                </span>
                Live Stream
              </TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
              <TabsTrigger value="diagnostics">Diagnostics</TabsTrigger>
            </TabsList>

            <TabsContent value="live" className="mt-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-sm font-medium">Event Stream</CardTitle>
                  <div className="flex items-center gap-1.5 text-xs text-status-success">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-success opacity-75" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-status-success" />
                    </span>
                    Live
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <ScrollArea className="h-[480px]">
                    <div className="p-4 space-y-2">
                      {events.map((event) => (
                        <EventCard key={event.id} event={event} />
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Event History</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<Event>
                    columns={[
                      {
                        key: "type",
                        header: "Type",
                        cell: (event) => {
                          const Icon = eventIcons[event.type] || Radio;
                          return (
                            <div className="flex items-center gap-2">
                              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                                <Icon className="h-3.5 w-3.5 text-primary" />
                              </div>
                              <span className="text-xs font-medium">{event.type}</span>
                            </div>
                          );
                        },
                      },
                      {
                        key: "source",
                        header: "Source",
                        cell: (event) => (
                          <span className="text-xs text-muted-foreground">{event.source}</span>
                        ),
                      },
                      {
                        key: "correlationId",
                        header: "Correlation ID",
                        cell: (event) => (
                          <code className="font-mono text-[11px] text-status-info">{event.correlationId}</code>
                        ),
                      },
                      {
                        key: "severity",
                        header: "Severity",
                        cell: (event) => (
                          <Badge variant={severityBadgeVariant[event.severity]} className="text-[10px]">
                            {event.severity}
                          </Badge>
                        ),
                      },
                      {
                        key: "timestamp",
                        header: "Timestamp",
                        className: "text-right",
                        cell: (event) => (
                          <span className="text-xs tabular-nums text-muted-foreground">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </span>
                        ),
                      },
                    ]}
                    data={events}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="diagnostics" className="mt-4 space-y-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-info/10">
                      <BarChart3 className="h-5 w-5 text-status-info" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Total Events</p>
                      <p className="text-xl font-semibold">{events.length}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-error/10">
                      <AlertCircle className="h-5 w-5 text-status-error" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Errors</p>
                      <p className="text-xl font-semibold">{errorCount}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-warning/10">
                      <Zap className="h-5 w-5 text-status-warning" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Warnings</p>
                      <p className="text-xl font-semibold">{warningCount}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-status-success/10">
                      <Activity className="h-5 w-5 text-status-success" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Info / Debug</p>
                      <p className="text-xl font-semibold">{infoCount + debugCount}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Top Event Types</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {topEventTypes.map(([type, count]) => {
                      const Icon = eventIcons[type] || Radio;
                      const pct = ((count / events.length) * 100).toFixed(0);
                      return (
                        <div key={type} className="flex items-center gap-3">
                          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                            <Icon className="h-3.5 w-3.5 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-medium">{type}</span>
                              <span className="text-xs text-muted-foreground">{count} ({pct}%)</span>
                            </div>
                            <div className="h-1.5 w-full rounded-full bg-muted">
                              <div
                                className="h-full rounded-full bg-primary"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Severity Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { label: "Info", count: infoCount, color: "bg-status-info", dot: "running" as const },
                      { label: "Warning", count: warningCount, color: "bg-status-warning", dot: "warning" as const },
                      { label: "Error", count: errorCount, color: "bg-status-error", dot: "error" as const },
                      { label: "Debug", count: debugCount, color: "bg-status-pending", dot: "idle" as const },
                    ].map((item) => (
                      <div key={item.label} className="flex flex-col items-center gap-1.5 rounded-lg border p-3">
                        <StatusDot status={item.dot} />
                        <span className="text-xs text-muted-foreground">{item.label}</span>
                        <span className="text-lg font-semibold">{item.count}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}
