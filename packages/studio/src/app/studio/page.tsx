"use client";

import { useAppStore } from "@/stores/app-store";
import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { MetricChart } from "@/components/shared/metric-chart";
import { SectionHeader } from "@/components/shared/section-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Bot, GitBranch, Wrench, Cpu, Activity, ArrowRight,
  AlertTriangle, Server, Shield, Radio, Layers, CheckCircle2, Brain, BookOpen, Zap,
  Box, Container, GitFork,
} from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const quickNavItems = [
  { label: "Workspace Manager", href: "/studio/workspace", icon: Box, color: "text-blue-500" },
  { label: "Agent Designer", href: "/studio/agents", icon: Bot, color: "text-cyan-500" },
  { label: "Workflow Designer", href: "/studio/workflows", icon: GitBranch, color: "text-amber-500" },
  { label: "Tool Manager", href: "/studio/tools", icon: Wrench, color: "text-orange-500" },
  { label: "Extension Manager", href: "/studio/extensions", icon: Container, color: "text-purple-500" },
  { label: "Knowledge Explorer", href: "/studio/knowledge", icon: BookOpen, color: "text-green-500" },
  { label: "Memory Inspector", href: "/studio/memory", icon: Brain, color: "text-pink-500" },
  { label: "Security Center", href: "/studio/security", icon: Shield, color: "text-red-500" },
  { label: "AI Runtime", href: "/studio/ai", icon: Cpu, color: "text-indigo-500" },
  { label: "API Explorer", href: "/studio/api-explorer", icon: GitFork, color: "text-teal-500" },
];

export default function StudioDashboardPage() {
  const { stats } = useAppStore();
  const { data: metrics } = useData(() => api.dashboard.metrics());
  const { data: alerts } = useData(() => api.observability.alerts());
  const { data: infra } = useData(() => api.infrastructure.components());

  const defaultStats = {
    activeProjects: 12,
    activeAgents: 8,
    runningWorkflows: 4,
    totalTools: 24,
    activeExtensions: 9,
    platformHealth: "healthy" as const,
    uptime: 99.97,
    alerts: 2,
  };

  const s = stats || defaultStats;
  const weeklyActivity = metrics || [
    { label: "Mon", value: 24 },
    { label: "Tue", value: 18 },
    { label: "Wed", value: 32 },
    { label: "Thu", value: 27 },
    { label: "Fri", value: 15 },
    { label: "Sat", value: 8 },
    { label: "Sun", value: 12 },
  ];
  const activeAlerts = (alerts || []).filter(a => !a.acknowledged).slice(0, 4);
  const components = infra || [];
  const platformComponents = ["database", "cache", "vector-store", "message-broker"].map(type => components.find(c => c.type === type)).filter((c): c is NonNullable<typeof c> => c != null);

  return (
    <div className="pb-8">
      <PageHeader
        title="JARVIS Studio Dashboard"
        description="Engineering command center for the JARVIS AI Ecosystem"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
          <StatCard title="Active Agents" value={s.activeAgents} icon={Bot} trend={{ value: 2, positive: true }} />
          <StatCard title="Running Workflows" value={s.runningWorkflows} icon={GitBranch} />
          <StatCard title="Total Tools" value={s.totalTools} icon={Wrench} trend={{ value: 4, positive: true }} />
          <StatCard title="Active Extensions" value={s.activeExtensions} icon={Container} />
          <StatCard title="Platform Uptime" value={`${s.uptime}%`} icon={Activity} />
        </motion.div>

        <motion.div variants={itemVariants} className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium">Platform Health Overview</CardTitle>
              <Badge variant="outline" className="gap-1 text-xs">
                <StatusDot status={s.platformHealth} />
                <span className="capitalize">{s.platformHealth}</span>
              </Badge>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {platformComponents.length > 0 ? platformComponents.map((item) => {
                  const iconMap: Record<string, React.ElementType> = { database: Server, cache: Zap, "vector-store": Layers, "message-broker": Radio };
                  const Icon = iconMap[item.type as string] || Server;
                  return (
                    <div key={item.id as string} className="flex flex-col gap-2 rounded-lg border p-3">
                      <div className="flex items-center justify-between">
                        <Icon className="h-4 w-4 text-primary" />
                        <StatusDot status={(item.status as string) as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
                      </div>
                      <p className="text-xs font-medium">{item.name as string}</p>
                      <p className="text-[10px] text-muted-foreground capitalize">{item.status as string}</p>
                    </div>
                  );
                }) : (
                  <>
                    {["Database", "Cache", "Vector Store", "Message Broker"].map((label) => (
                      <div key={label} className="flex flex-col gap-2 rounded-lg border p-3 animate-pulse">
                        <div className="h-4 w-4 rounded bg-muted" />
                        <p className="text-xs font-medium">{label}</p>
                        <p className="text-[10px] text-muted-foreground">Loading...</p>
                      </div>
                    ))}
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Quick Navigation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {quickNavItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-accent transition-colors"
                >
                  <item.icon className={`h-3.5 w-3.5 ${item.color}`} />
                  <span>{item.label}</span>
                </Link>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants} className="grid gap-4 lg:grid-cols-2">
          <MetricChart title="Weekly Activity (Workflow Executions)" data={weeklyActivity} />
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
              <Button variant="ghost" size="sm" className="text-xs h-7">
                View all <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activeAlerts.length > 0 ? activeAlerts.map((alert) => (
                  <div key={alert.id} className="flex items-start gap-2">
                    <div className={`flex h-7 w-7 items-center justify-center rounded-full shrink-0 ${
                      alert.severity === "critical" ? "bg-status-error/10" :
                      alert.severity === "warning" ? "bg-status-warning/10" : "bg-status-success/10"
                    }`}>
                      <AlertTriangle className={`h-3.5 w-3.5 ${
                        alert.severity === "critical" ? "text-status-error" :
                        alert.severity === "warning" ? "text-status-warning" : "text-status-success"
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs">{alert.title}: {alert.message}</p>
                      <p className="text-[10px] text-muted-foreground">{String(alert.timestamp)}</p>
                    </div>
                  </div>
                )) : (
                  <div className="flex items-center gap-2 py-2">
                    <CheckCircle2 className="h-4 w-4 text-status-success" />
                    <p className="text-xs text-muted-foreground">No active alerts</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <SectionHeader
            title="Engineering Summary"
            description="Key engineering metrics"
            action={{ label: "View Details", href: "/studio/observability" }}
            className="mb-3"
          />
          <div className="grid gap-3 sm:grid-cols-3">
            {[
              { icon: CheckCircle2, label: "API Gateway Status", value: "All endpoints operational", color: "text-status-success" },
              { icon: Layers, label: "Active Connections", value: "14 services connected", color: "text-primary" },
              { icon: Activity, label: "Avg API Latency", value: "124ms p95", color: "text-status-info" },
            ].map((item) => (
              <Card key={item.label}>
                <CardContent className="p-3 flex items-center gap-3">
                  <item.icon className={`h-5 w-5 ${item.color}`} />
                  <div>
                    <p className="text-[10px] text-muted-foreground">{item.label}</p>
                    <p className="text-xs font-medium">{item.value}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
