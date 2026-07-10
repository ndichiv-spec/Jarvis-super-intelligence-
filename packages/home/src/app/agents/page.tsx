"use client";

import { useState, useEffect } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/shared/status-dot";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/shared/empty-state";
import { Bot, Plus, Activity, Cpu, Loader2, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

const API = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

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

const statusColors: Record<string, string> = {
  ready: "bg-status-success/10 text-status-success",
  busy: "bg-status-warning/10 text-status-warning",
  idle: "bg-muted text-muted-foreground",
  error: "bg-status-error/10 text-status-error",
  disabled: "bg-muted text-muted-foreground",
  created: "bg-muted text-muted-foreground",
  initializing: "bg-status-pending/10 text-status-pending",
  paused: "bg-status-pending/10 text-status-pending",
  suspended: "bg-status-error/10 text-status-error",
  failed: "bg-status-error/10 text-status-error",
  recovering: "bg-status-warning/10 text-status-warning",
  retired: "bg-muted text-muted-foreground",
};

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState("all");

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`${API}/agents/`)
      .then((r) => r.json())
      .then((data) => {
        setAgents(data.agents || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const filtered = tab === "all" ? agents : agents.filter((a) => a.status === tab);

  if (loading) {
    return (
      <div className="pb-8">
        <PageHeader title="Agent Center" description="Monitor and manage your AI agents" />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pb-8">
        <PageHeader title="Agent Center" description="Monitor and manage your AI agents" />
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
        title="Agent Center"
        description="Monitor and manage your AI agents"
        actions={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Agent
          </Button>
        }
      />

      <div className="px-6 space-y-4">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="all">All ({agents.length})</TabsTrigger>
            <TabsTrigger value="ready">Ready</TabsTrigger>
            <TabsTrigger value="busy">Busy</TabsTrigger>
            <TabsTrigger value="paused">Paused</TabsTrigger>
            <TabsTrigger value="failed">Failed</TabsTrigger>
          </TabsList>

          <TabsContent value={tab} className="mt-4">
            {filtered.length === 0 ? (
              <EmptyState icon={Bot} title="No agents found" description="No agents match the current filter" />
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {filtered.map((agent, i) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <Card className="h-full">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                              <Bot className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <CardTitle className="text-base">{agent.name}</CardTitle>
                              <CardDescription className="text-xs">{agent.role}</CardDescription>
                            </div>
                          </div>
                          <Badge variant="outline" className={statusColors[agent.status] || ""}>
                            <StatusDot status={agent.status as "error" | "active" | "success" | "warning" | "pending" | "running" | "idle" | "busy" | "healthy" | "degraded" | "critical" | "inactive"} className="mr-1" />
                            {agent.status}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-muted-foreground">{agent.description}</p>
                        <div className="flex flex-wrap gap-1">
                          {agent.capabilities.map((cap) => (
                            <Badge key={cap.name} variant="secondary" className="text-[10px]">
                              {cap.name}
                            </Badge>
                          ))}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="rounded-md border p-2 text-center">
                            <p className="text-muted-foreground">Workspace</p>
                            <p className="font-medium">{agent.workspace}</p>
                          </div>
                          <div className="rounded-md border p-2 text-center">
                            <p className="text-muted-foreground">Version</p>
                            <p className="font-medium">{agent.version}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
