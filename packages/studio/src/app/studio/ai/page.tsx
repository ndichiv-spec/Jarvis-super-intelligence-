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
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  Cpu, Server, Route, DollarSign, Activity,
  CheckCircle2, AlertTriangle, XCircle,
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

type ProviderStatus = "healthy" | "degraded" | "error";

interface Provider {
  id: string;
  name: string;
  type: string;
  status: ProviderStatus;
  modelCount: number;
  avgLatency: string;
  totalCalls: number;
}

interface AIModel {
  id: string;
  name: string;
  provider: string;
  capabilities: string[];
  status: "active" | "deprecated" | "experimental";
  tokensIn: number;
  tokensOut: number;
  cost: string;
}

interface RouteConfig {
  model: string;
  provider: string;
  priority: number;
}

const providers: Provider[] = [
  { id: "p1", name: "OpenAI", type: "Cloud API", status: "healthy", modelCount: 3, avgLatency: "1.2s", totalCalls: 45231 },
  { id: "p2", name: "Azure", type: "Cloud API", status: "healthy", modelCount: 3, avgLatency: "0.9s", totalCalls: 32108 },
  { id: "p3", name: "Anthropic", type: "Cloud API", status: "degraded", modelCount: 2, avgLatency: "2.4s", totalCalls: 18975 },
];

const models: AIModel[] = [
  { id: "m1", name: "gpt-4o", provider: "OpenAI", capabilities: ["chat", "vision", "code"], status: "active", tokensIn: 125000000, tokensOut: 32000000, cost: "$2.50/Mtok" },
  { id: "m2", name: "gpt-4o-mini", provider: "OpenAI", capabilities: ["chat", "code"], status: "active", tokensIn: 89000000, tokensOut: 18000000, cost: "$0.15/Mtok" },
  { id: "m3", name: "o1", provider: "OpenAI", capabilities: ["reasoning", "chat"], status: "experimental", tokensIn: 4500000, tokensOut: 1200000, cost: "$15.00/Mtok" },
  { id: "m4", name: "gpt-4o", provider: "Azure", capabilities: ["chat", "vision", "code"], status: "active", tokensIn: 98000000, tokensOut: 25000000, cost: "$2.50/Mtok" },
  { id: "m5", name: "gpt-4o-mini", provider: "Azure", capabilities: ["chat", "code"], status: "active", tokensIn: 72000000, tokensOut: 14000000, cost: "$0.15/Mtok" },
  { id: "m6", name: "o1-preview", provider: "Azure", capabilities: ["reasoning", "chat"], status: "deprecated", tokensIn: 2100000, tokensOut: 600000, cost: "$15.00/Mtok" },
  { id: "m7", name: "claude-3.5-sonnet", provider: "Anthropic", capabilities: ["chat", "vision", "code"], status: "active", tokensIn: 67000000, tokensOut: 15000000, cost: "$3.00/Mtok" },
  { id: "m8", name: "claude-3-haiku", provider: "Anthropic", capabilities: ["chat", "code"], status: "active", tokensIn: 41000000, tokensOut: 9200000, cost: "$0.25/Mtok" },
];

const routingTable: RouteConfig[] = [
  { model: "gpt-4o", provider: "Azure (primary)", priority: 1 },
  { model: "gpt-4o", provider: "OpenAI (fallback)", priority: 2 },
  { model: "gpt-4o-mini", provider: "Azure (primary)", priority: 1 },
  { model: "gpt-4o-mini", provider: "OpenAI (fallback)", priority: 2 },
  { model: "claude-3.5-sonnet", provider: "Anthropic (primary)", priority: 1 },
  { model: "claude-3-haiku", provider: "Anthropic (primary)", priority: 1 },
  { model: "o1", provider: "OpenAI", priority: 1 },
  { model: "o1-preview", provider: "Azure", priority: 1 },
];

const usageData = [
  { label: "Mon", value: 2480000 },
  { label: "Tue", value: 3120000 },
  { label: "Wed", value: 2850000 },
  { label: "Thu", value: 4210000 },
  { label: "Fri", value: 3680000 },
  { label: "Sat", value: 1850000 },
  { label: "Sun", value: 1420000 },
];

const TOTAL_COST = "$2,847.32";

const providerColumns: Column<Provider>[] = [
  {
    key: "name",
    header: "Name",
    cell: (p) => (
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
          <Server className="h-3.5 w-3.5 text-primary" />
        </div>
        <span className="font-medium">{p.name}</span>
      </div>
    ),
  },
  {
    key: "type",
    header: "Type",
    cell: (p) => <span className="text-xs text-muted-foreground">{p.type}</span>,
  },
  {
    key: "status",
    header: "Status",
    cell: (p) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={p.status} />
        <span className="text-xs capitalize text-muted-foreground">{p.status}</span>
      </div>
    ),
  },
  {
    key: "modelCount",
    header: "Models",
    className: "text-right",
    cell: (p) => <span className="text-xs tabular-nums">{p.modelCount}</span>,
  },
  {
    key: "avgLatency",
    header: "Avg Latency",
    className: "text-right",
    cell: (p) => <span className="text-xs font-mono text-muted-foreground">{p.avgLatency}</span>,
  },
  {
    key: "totalCalls",
    header: "Total Calls",
    className: "text-right",
    cell: (p) => <span className="text-xs tabular-nums">{p.totalCalls.toLocaleString()}</span>,
  },
];

const modelColumns: Column<AIModel>[] = [
  {
    key: "name",
    header: "Name",
    cell: (m) => (
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
          <Cpu className="h-3.5 w-3.5 text-primary" />
        </div>
        <span className="font-medium font-mono text-xs">{m.name}</span>
      </div>
    ),
  },
  {
    key: "provider",
    header: "Provider",
    cell: (m) => <span className="text-xs text-muted-foreground">{m.provider}</span>,
  },
  {
    key: "capabilities",
    header: "Capabilities",
    cell: (m) => (
      <div className="flex flex-wrap gap-1">
        {m.capabilities.map((cap) => (
          <Badge key={cap} variant="secondary" className="text-[10px]">{cap}</Badge>
        ))}
      </div>
    ),
  },
  {
    key: "status",
    header: "Status",
    cell: (m) => (
      <Badge
        variant={
          m.status === "active" ? "success" :
          m.status === "experimental" ? "warning" : "secondary"
        }
        className="text-[10px]"
      >
        {m.status}
      </Badge>
    ),
  },
  {
    key: "tokensIn",
    header: "Tokens In",
    className: "text-right",
    cell: (m) => <span className="text-xs tabular-nums">{(m.tokensIn / 1_000_000).toFixed(1)}M</span>,
  },
  {
    key: "tokensOut",
    header: "Tokens Out",
    className: "text-right",
    cell: (m) => <span className="text-xs tabular-nums">{(m.tokensOut / 1_000_000).toFixed(1)}M</span>,
  },
  {
    key: "cost",
    header: "Cost",
    className: "text-right",
    cell: (m) => <span className="text-xs font-mono text-muted-foreground">{m.cost}</span>,
  },
];

export default function AIRuntimePage() {
  const { data: providerData, loading: provLoading, error: provError } = useData(() => api.ai.providers());
  const displayProviders: Provider[] = providerData
    ? providerData.map((p) => ({
        id: p.id,
        name: p.name,
        type: p.type,
        status: p.status,
        modelCount: p.models.length,
        avgLatency: `${p.latency}ms`,
        totalCalls: p.usage.totalCalls,
      }))
    : providers;
  const displayModels: AIModel[] = providerData
    ? providerData.flatMap((p) =>
        p.models.map((m) => ({
          id: m.id,
          name: m.name,
          provider: p.name,
          capabilities: m.capabilities,
          status: m.status === "available" ? "active" as const : "experimental" as const,
          tokensIn: m.usage.tokensIn,
          tokensOut: m.usage.tokensOut,
          cost: `$${(m.usage.cost / 1_000_000).toFixed(2)}/Mtok`,
        })),
      )
    : models;

  return (
    <div className="pb-8">
      <PageHeader
        title="AI Runtime Manager"
        description="Manage AI providers, models, and routing configuration"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Active Providers" value={displayProviders.filter((p) => p.status === "healthy").length} icon={Server} description={`${displayProviders.length} total configured`} />
          <StatCard title="Total Models" value={displayModels.length} icon={Cpu} description={`${displayModels.filter((m) => m.status === "active").length} active`} />
          <StatCard title="Total Calls Today" value={displayProviders.reduce((s, p) => s + p.totalCalls, 0).toLocaleString()} icon={Activity} trend={{ value: 12, positive: true }} />
          <StatCard title="Avg Latency" value="1.5s" icon={Activity} description="Across all providers" trend={{ value: 8, positive: false }} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="providers">
            <TabsList>
              <TabsTrigger value="providers" className="gap-1.5">
                <Server className="h-3.5 w-3.5" />
                Providers
              </TabsTrigger>
              <TabsTrigger value="models" className="gap-1.5">
                <Cpu className="h-3.5 w-3.5" />
                Models
              </TabsTrigger>
              <TabsTrigger value="routing" className="gap-1.5">
                <Route className="h-3.5 w-3.5" />
                Routing
              </TabsTrigger>
              <TabsTrigger value="usage" className="gap-1.5">
                <Activity className="h-3.5 w-3.5" />
                Usage
              </TabsTrigger>
            </TabsList>

            <TabsContent value="providers" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">AI Providers</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<Provider>
                    columns={providerColumns}
                    data={displayProviders}
                    emptyMessage="No providers configured"
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="models" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Model Catalog</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<AIModel>
                    columns={modelColumns}
                    data={displayModels}
                    emptyMessage="No models configured"
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="routing" className="mt-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium">Default Configuration</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between rounded-lg border p-3">
                      <div className="flex items-center gap-2">
                        <Server className="h-4 w-4 text-primary" />
                        <span className="text-xs font-medium">Default Provider</span>
                      </div>
                      <Badge variant="outline" className="text-xs">Azure (gpt-4o)</Badge>
                    </div>
                    <div className="flex items-center justify-between rounded-lg border p-3">
                      <div className="flex items-center gap-2">
                        <Route className="h-4 w-4 text-primary" />
                        <span className="text-xs font-medium">Fallback Strategy</span>
                      </div>
                      <Badge variant="outline" className="text-xs">Priority-based</Badge>
                    </div>
                    <div className="flex items-center justify-between rounded-lg border p-3">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-primary" />
                        <span className="text-xs font-medium">Health Check Interval</span>
                      </div>
                      <Badge variant="outline" className="text-xs">30 seconds</Badge>
                    </div>
                    <div className="flex items-center justify-between rounded-lg border p-3">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-status-warning" />
                        <span className="text-xs font-medium">Circuit Breaker Threshold</span>
                      </div>
                      <Badge variant="outline" className="text-xs">5 failures / 60s</Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium">Per-Model Routing</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-studio-border">
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Model</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Provider</th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">Priority</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-studio-border">
                        {routingTable.map((r) => (
                          <tr key={`${r.model}-${r.provider}`} className="transition-colors hover:bg-studio-hover">
                            <td className="px-4 py-3 text-sm">
                              <span className="font-mono text-xs">{r.model}</span>
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className="text-xs text-muted-foreground">{r.provider}</span>
                            </td>
                            <td className="px-4 py-3 text-sm text-right">
                              <Badge
                                variant={r.priority === 1 ? "success" : "secondary"}
                                className="text-[10px]"
                              >
                                P{r.priority}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="usage" className="mt-4">
              <div className="grid gap-3 sm:grid-cols-3 mb-4">
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Activity className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Total Tokens (In)</p>
                      <p className="text-xl font-semibold">{displayModels.reduce((s, m) => s + m.tokensIn, 0) > 0 ? `${(displayModels.reduce((s, m) => s + m.tokensIn, 0) / 1_000_000).toFixed(1)}M` : "—"}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Activity className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Total Tokens (Out)</p>
                      <p className="text-xl font-semibold">{displayModels.reduce((s, m) => s + m.tokensOut, 0) > 0 ? `${(displayModels.reduce((s, m) => s + m.tokensOut, 0) / 1_000_000).toFixed(1)}M` : "—"}</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <DollarSign className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Estimated Cost</p>
                      <p className="text-xl font-semibold">{TOTAL_COST}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
              <MetricChart title="Token Usage (Daily)" data={usageData} />
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}
