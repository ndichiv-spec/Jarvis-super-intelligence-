"use client";

import { useAppStore } from "@/stores/app-store";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { MetricChart } from "@/components/shared/metric-chart";
import { SectionHeader } from "@/components/shared/section-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Bot,
  FolderKanban,
  MessageSquare,
  Zap,
  Brain,
  BookOpen,
  Bell,
  Activity,
  ArrowRight,
  Sparkles,
  Clock,
  TrendingUp,
  Layers,
  Cpu,
  BarChart3,
  GitBranch,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

const weeklyActivity = [
  { label: "Mon", value: 24 },
  { label: "Tue", value: 18 },
  { label: "Wed", value: 32 },
  { label: "Thu", value: 27 },
  { label: "Fri", value: 15 },
  { label: "Sat", value: 8 },
  { label: "Sun", value: 12 },
];

const usageData = [
  { label: "Week 1", value: 156 },
  { label: "Week 2", value: 189 },
  { label: "Week 3", value: 142 },
  { label: "Week 4", value: 214 },
];

export default function DashboardPage() {
  const { stats } = useAppStore();

  const defaultStats = {
    activeProjects: 12,
    activeAgents: 8,
    runningAutomations: 4,
    recentConversations: 24,
    memoryItems: 342,
    knowledgeDocuments: 156,
    unreadNotifications: 3,
    platformHealth: "healthy" as const,
    uptime: 99.97,
  };

  const s = stats || defaultStats;

  const quickActions = [
    { label: "New Conversation", icon: MessageSquare, href: "/workspace", primary: true },
    { label: "New Project", icon: FolderKanban, href: "/projects" },
    { label: "Browse Knowledge", icon: BookOpen, href: "/knowledge" },
    { label: "View Memory", icon: Brain, href: "/memory" },
  ];

  return (
    <div className="pb-8">
      <PageHeader
        title="Home"
        description="Welcome back, Alex. Here is your ecosystem overview."
        actions={
          <Button>
            <Sparkles className="mr-2 h-4 w-4" />
            Quick Start
          </Button>
        }
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6">
        <motion.div variants={itemVariants} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Active Projects" value={s.activeProjects} icon={FolderKanban} trend={{ value: 8, positive: true }} />
          <StatCard title="Active Agents" value={s.activeAgents} icon={Bot} trend={{ value: 2, positive: true }} />
          <StatCard title="Running Automations" value={s.runningAutomations} icon={Zap} />
          <StatCard title="Recent Conversations" value={s.recentConversations} icon={MessageSquare} trend={{ value: 12, positive: true }} />
        </motion.div>

        <motion.div variants={itemVariants} className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">System Health</CardTitle>
              <Badge variant="outline" className="gap-1">
                <StatusDot status={s.platformHealth} />
                <span className="capitalize">{s.platformHealth}</span>
                <span className="ml-1 text-muted-foreground">Uptime: {s.uptime}%</span>
              </Badge>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: "Memory Items", value: s.memoryItems, icon: Brain, sub: "Active" },
                  { label: "Knowledge Documents", value: s.knowledgeDocuments, icon: BookOpen, sub: "6 collections" },
                  { label: "Active Automations", value: s.runningAutomations, icon: Zap, sub: "3 scheduled" },
                  { label: "Platform Load", value: "24%", icon: Cpu, sub: "Normal" },
                ].map((item) => (
                  <div key={item.label} className="flex flex-col gap-2 rounded-lg border p-3">
                    <div className="flex items-center gap-2">
                      <item.icon className="h-4 w-4 text-primary" />
                      <span className="text-xs text-muted-foreground">{item.label}</span>
                    </div>
                    <p className="text-xl font-semibold">{item.value}</p>
                    <p className="text-xs text-muted-foreground">{item.sub}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickActions.map((action) => (
                <Button
                  key={action.label}
                  variant={action.primary ? "default" : "outline"}
                  className="w-full justify-start"
                  asChild
                >
                  <a href={action.href}>
                    <action.icon className="mr-2 h-4 w-4" />
                    {action.label}
                  </a>
                </Button>
              ))}
              <Separator className="my-2" />
              <Button variant="ghost" className="w-full justify-start text-muted-foreground" asChild>
                <a href="/settings">
                  <Bell className="mr-2 h-4 w-4" />
                  {s.unreadNotifications} Unread Notifications
                </a>
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants} className="grid gap-4 lg:grid-cols-2">
          <MetricChart title="Weekly Activity" data={weeklyActivity} />
          <MetricChart title="Monthly Usage (API Calls)" data={usageData} color="hsl(var(--status-info))" />
        </motion.div>

        <motion.div variants={itemVariants} className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Recent Activity</CardTitle>
              <Button variant="ghost" size="sm">
                View all <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { icon: MessageSquare, text: "Concluded analysis of Q2 metrics", time: "5m ago", type: "conversation", color: "text-blue-500" },
                  { icon: Bot, text: "WebScraper agent completed task", time: "12m ago", type: "agent", color: "text-cyan-500" },
                  { icon: Zap, text: "Scheduled backup workflow ran successfully", time: "1h ago", type: "automation", color: "text-amber-500" },
                  { icon: FolderKanban, text: "Updated project 'Market Analysis'", time: "2h ago", type: "project", color: "text-orange-500" },
                  { icon: Brain, text: "New memory: User prefers dark theme", time: "3h ago", type: "memory", color: "text-purple-500" },
                  { icon: BookOpen, text: "Added document: Security Best Practices", time: "5h ago", type: "knowledge", color: "text-green-500" },
                ].map((activity, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted shrink-0">
                      <activity.icon className={`h-4 w-4 ${activity.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate">{activity.text}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                    <Badge variant="outline" className="shrink-0 text-[10px]">
                      {activity.type}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Active Agents</CardTitle>
              <Button variant="ghost" size="sm">
                View all <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "CodeAssistant", task: "Refactoring auth module", status: "busy" as const, icon: Bot, tasks: 342 },
                  { name: "DataAnalyzer", task: "Processing Q2 reports", status: "busy" as const, icon: BarChart3, tasks: 156 },
                  { name: "WebScraper", task: "Monitoring price changes", status: "active" as const, icon: GitBranch, tasks: 891 },
                  { name: "DocGenerator", task: "Writing API docs", status: "idle" as const, icon: BookOpen, tasks: 234 },
                  { name: "SecurityScanner", task: undefined, status: "error" as const, icon: AlertTriangle, tasks: 67 },
                  { name: "ResearchAssistant", task: "Compiling market research", status: "active" as const, icon: Brain, tasks: 445 },
                ].map((agent) => (
                  <div key={agent.name} className="flex items-center gap-3 rounded-lg border p-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
                      <agent.icon className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium">{agent.name}</p>
                        <span className="text-xs text-muted-foreground">{agent.tasks} tasks</span>
                      </div>
                      {agent.task && (
                        <p className="text-xs text-muted-foreground truncate">{agent.task}</p>
                      )}
                    </div>
                    <StatusDot status={agent.status} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <SectionHeader
            title="Platform Summary"
            description="Key metrics at a glance"
            action={{ label: "View Details", href: "/settings" }}
            className="mb-4"
          />
          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { icon: CheckCircle2, label: "System Status", value: "Operational", color: "text-status-success" },
              { icon: Layers, label: "Total Extensions", value: "9 installed", color: "text-primary" },
              { icon: Activity, label: "API Latency", value: "124ms avg", color: "text-status-info" },
            ].map((item) => (
              <Card key={item.label}>
                <CardContent className="p-4 flex items-center gap-3">
                  <item.icon className={`h-5 w-5 ${item.color}`} />
                  <div>
                    <p className="text-xs text-muted-foreground">{item.label}</p>
                    <p className="text-sm font-medium">{item.value}</p>
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
