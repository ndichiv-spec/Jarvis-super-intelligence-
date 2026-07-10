"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatusDot } from "@/components/shared/status-dot";
import { DataTable } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  Bot, Activity, Shield, Cpu, Search, FileText, BarChart3,
  CheckCircle2, AlertTriangle, Zap, Loader2, AlertCircle,
} from "lucide-react";
import { motion } from "framer-motion";

interface AgentData {
  id: string;
  name: string;
  role: string;
  description: string;
  status: string;
  capabilities: { name: string; description: string }[];
  version: string;
  owner: string;
  workspace: string;
  created_at: string;
  updated_at: string;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const agentIcons: Record<string, typeof Bot> = {
  Planner: Bot,
  Coding: Cpu,
  Research: Search,
  Memory: Activity,
  Automation: Zap,
  Desktop: Cpu,
  WebIntelligence: Search,
  Vision: BarChart3,
  Voice: Activity,
  Communication: Bot,
};

const healthyStatuses = new Set(["ready", "active"]);
const degradedStatuses = new Set(["busy", "idle", "paused"]);
const errorStatuses = new Set(["failed", "error", "suspended", "recovering"]);

function getCapabilityStatus(agents: AgentData[], capName: string): "healthy" | "degraded" | "error" {
  const matched = agents.filter((a) => a.capabilities.some((c) => c.name === capName));
  if (matched.length === 0) return "error";
  const anyFailed = matched.some((a) => errorStatuses.has(a.status));
  const anyDegraded = matched.some((a) => degradedStatuses.has(a.status));
  if (anyFailed) return "error";
  if (anyDegraded) return "degraded";
  return "healthy";
}

export default function AgentDesignerPage() {
  const { data: rawAgents, loading, error } = useData(() => api.agents.list());
  const agents: AgentData[] = (rawAgents || []).map((a) => ({
    id: a.id,
    name: a.name,
    role: a.model || "assistant",
    description: a.description,
    status: a.status,
    capabilities: a.capabilities.map((c) => ({ name: c, description: "" })),
    version: a.version,
    owner: "",
    workspace: "",
    created_at: "",
    updated_at: "",
  }));

  const capabilityCards = [
    { name: "planning", description: "Create and manage plans", icon: Bot },
    { name: "programming", description: "Write, review, and refactor code", icon: Cpu },
    { name: "research", description: "Deep research and summarization", icon: Search },
    { name: "memory_management", description: "Manage memory and knowledge", icon: Activity },
    { name: "automation", description: "Automate workflows and pipelines", icon: Zap },
    { name: "web_scraping", description: "Crawl, extract, and monitor web content", icon: Search },
  ];

  const healthMetrics = [
    { label: "Ready Agents", value: agents.filter((a) => a.status === "ready" || a.status === "active").length, icon: CheckCircle2, color: "text-status-success" },
    { label: "Paused Agents", value: agents.filter((a) => a.status === "paused" || a.status === "idle").length, icon: Activity, color: "text-status-pending" },
    { label: "Busy Agents", value: agents.filter((a) => a.status === "busy").length, icon: Zap, color: "text-status-warning" },
    { label: "Failed Agents", value: agents.filter((a) => errorStatuses.has(a.status)).length, icon: AlertTriangle, color: "text-status-error" },
  ];

  if (loading) {
    return (
      <div className="pb-8">
        <PageHeader title="Agent Designer" description="Design, configure, and monitor your AI agents" />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pb-8">
        <PageHeader title="Agent Designer" description="Design, configure, and monitor your AI agents" />
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <AlertCircle className="h-10 w-10 text-status-error" />
          <p className="text-sm text-muted-foreground">Failed to load agents: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-8">
      <PageHeader
        title="Agent Designer"
        description="Design, configure, and monitor your AI agents"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants}>
          <Tabs defaultValue="catalog">
            <TabsList>
              <TabsTrigger value="catalog">Catalog</TabsTrigger>
              <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
              <TabsTrigger value="health">Health</TabsTrigger>
            </TabsList>

            <TabsContent value="catalog" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Agent Catalog</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<AgentData>
                    columns={[
                      {
                        key: "name",
                        header: "Agent",
                        cell: (agent) => {
                          const Icon = agentIcons[agent.name] || Bot;
                          return (
                            <div className="flex items-center gap-2">
                              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                                <Icon className="h-3.5 w-3.5 text-primary" />
                              </div>
                              <span className="font-medium">{agent.name}</span>
                            </div>
                          );
                        },
                      },
                      {
                        key: "status",
                        header: "Status",
                        cell: (agent) => (
                          <div className="flex items-center gap-1.5">
                            <StatusDot status={agent.status as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
                            <span className="text-xs capitalize text-muted-foreground">{agent.status}</span>
                          </div>
                        ),
                      },
                      {
                        key: "role",
                        header: "Role",
                        cell: (agent) => (
                          <span className="text-xs font-mono text-muted-foreground">{agent.role}</span>
                        ),
                      },
                      {
                        key: "capabilities",
                        header: "Capabilities",
                        cell: (agent) => (
                          <div className="flex flex-wrap gap-1">
                            {agent.capabilities.map((cap) => (
                              <Badge key={cap.name} variant="secondary" className="text-[10px]">
                                {cap.name}
                              </Badge>
                            ))}
                          </div>
                        ),
                      },
                      {
                        key: "workspace",
                        header: "Workspace",
                        className: "text-right",
                        cell: (agent) => (
                          <span className="text-xs tabular-nums">{agent.workspace}</span>
                        ),
                      },
                      {
                        key: "version",
                        header: "Version",
                        className: "text-right",
                        cell: (agent) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{agent.version}</span>
                        ),
                      },
                    ]}
                    data={agents}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="capabilities" className="mt-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {capabilityCards.map((cap) => {
                  const capStatus = getCapabilityStatus(agents, cap.name);
                  const count = agents.filter((a) => a.capabilities.some((c) => c.name === cap.name)).length;
                  return (
                    <Card key={cap.name}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                            <cap.icon className="h-4.5 w-4.5 text-primary" />
                          </div>
                          <StatusDot status={capStatus} />
                        </div>
                        <h4 className="text-sm font-medium mb-0.5 capitalize">{cap.name.replace(/_/g, " ")}</h4>
                        <p className="text-xs text-muted-foreground mb-3">{cap.description}</p>
                        <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                          <span>{count} agent{count !== 1 ? "s" : ""}</span>
                          <Badge
                            variant={
                              capStatus === "healthy" ? "success" :
                              capStatus === "degraded" ? "warning" : "destructive"
                            }
                            className="text-[10px]"
                          >
                            {capStatus}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="health" className="mt-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-4">
                {healthMetrics.map((metric) => (
                  <Card key={metric.label}>
                    <CardContent className="p-4 flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <metric.icon className={`h-5 w-5 ${metric.color}`} />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">{metric.label}</p>
                        <p className="text-xl font-semibold">{metric.value}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Agent Status Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {agents.map((agent) => {
                      const Icon = agentIcons[agent.name] || Bot;
                      return (
                        <div key={agent.id} className="flex items-center gap-3 rounded-lg border p-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                            <Icon className="h-4 w-4 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium">{agent.name}</span>
                              <StatusDot status={agent.status as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
                              <span className="text-xs capitalize text-muted-foreground">{agent.status}</span>
                            </div>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              {agent.role} &middot; {agent.capabilities.length} capabilities &middot; v{agent.version}
                            </p>
                          </div>
                          <div className="hidden sm:flex items-center gap-1.5">
                            <Badge
                              variant={
                                agent.status === "ready" || agent.status === "active" ? "success" :
                                agent.status === "paused" || agent.status === "idle" ? "secondary" :
                                agent.status === "busy" ? "warning" : "destructive"
                              }
                              className="text-[10px]"
                            >
                              {agent.status}
                            </Badge>
                          </div>
                        </div>
                      );
                    })}
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
