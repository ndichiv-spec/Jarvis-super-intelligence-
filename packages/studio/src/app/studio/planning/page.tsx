"use client";

import { useState } from "react";
import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable, type Column } from "@/components/shared/data-table";
import { StatusDot } from "@/components/shared/status-dot";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Brain,
  Target,
  GitBranch,
  ListChecks,
  Timer,
  PlayCircle,
  PauseCircle,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  UserCheck,
  Layers,
  TrendingUp,
  Plus,
  Settings,
} from "lucide-react";
import { motion } from "framer-motion";

interface PlanItem {
  id: string;
  objective: string;
  status: string;
  category: string;
  complexity: string;
  taskCount: number;
  completion: number;
  createdAt: string;
}

interface TaskDetail {
  id: string;
  title: string;
  description: string;
  status: string;
  assignedAgent: string;
  effort: number;
  deps: string[];
}

const MOCK_PLANS: PlanItem[] = [
  { id: "p1", objective: "Build inventory management platform", status: "executing", category: "application", complexity: "complex", taskCount: 9, completion: 35, createdAt: "2h ago" },
  { id: "p2", objective: "Migrate legacy auth to OAuth 2.0", status: "validated", category: "security", complexity: "moderate", taskCount: 6, completion: 0, createdAt: "1d ago" },
  { id: "p3", objective: "Implement CI/CD pipeline", status: "completed", category: "devops", complexity: "moderate", taskCount: 7, completion: 100, createdAt: "3d ago" },
];

const MOCK_TASKS: TaskDetail[] = [
  { id: "t1", title: "Gather Requirements", description: "Collect functional requirements", status: "completed", assignedAgent: "research", effort: 4, deps: [] },
  { id: "t2", title: "Design Architecture", description: "System architecture design", status: "completed", assignedAgent: "engineering", effort: 6, deps: ["t1"] },
  { id: "t3", title: "Design Database Schema", description: "Database schema design", status: "running", assignedAgent: "engineering", effort: 4, deps: ["t1"] },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const planColumns: Column<PlanItem>[] = [
  { key: "objective", header: "Objective", cell: (item: PlanItem) => <span className="font-medium">{item.objective}</span> },
  { key: "status", header: "Status", cell: (item: PlanItem) => <StatusDot status={item.status as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} /> },
  { key: "category", header: "Category", cell: (item: PlanItem) => <span>{item.category}</span> },
  { key: "complexity", header: "Complexity", cell: (item: PlanItem) => <Badge variant="outline">{item.complexity}</Badge> },
  { key: "taskCount", header: "Tasks", cell: (item: PlanItem) => <span>{item.taskCount}</span> },
  { key: "completion", header: "Progress", cell: (item: PlanItem) => <span>{item.completion}%</span> },
  { key: "createdAt", header: "Created", cell: (item: PlanItem) => <span>{item.createdAt}</span> },
];

export default function StudioPlanningPage() {
  const [activeTab, setActiveTab] = useState("plans");
  const { data: plansData, loading, error } = useData(() => api.planning.list());
  const plans = (plansData || MOCK_PLANS) as PlanItem[];

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <PageHeader
        title="Planning Workspace"
        description="Cognitive planning engine — analyze, decompose, schedule, and monitor execution"
      />

      <div className="flex-1 overflow-auto p-6">
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="max-w-7xl mx-auto space-y-6">
          <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
            <StatCard title="Active Plans" value="3" icon={Brain} trend={{ value: 2, positive: true }} />
            <StatCard title="Total Tasks" value="22" icon={ListChecks} />
            <StatCard title="Completed" value="14" icon={CheckCircle2} trend={{ value: 64, positive: true }} />
            <StatCard title="Avg. Complexity" value="Moderate" icon={TrendingUp} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList>
                <TabsTrigger value="plans">
                  <Target className="h-4 w-4 mr-1.5" /> Plans
                </TabsTrigger>
                <TabsTrigger value="tasks">
                  <ListChecks className="h-4 w-4 mr-1.5" /> Task Inspector
                </TabsTrigger>
                <TabsTrigger value="graph">
                  <GitBranch className="h-4 w-4 mr-1.5" /> Dependency Explorer
                </TabsTrigger>
                <TabsTrigger value="agents">
                  <UserCheck className="h-4 w-4 mr-1.5" /> Agent Allocation
                </TabsTrigger>
                <TabsTrigger value="timeline">
                  <Timer className="h-4 w-4 mr-1.5" /> Execution Timeline
                </TabsTrigger>
              </TabsList>

              <TabsContent value="plans" className="pt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">{plans.length} plans</p>
                  <Button size="sm" className="gap-1.5">
                    <Plus className="h-4 w-4" /> New Plan
                  </Button>
                </div>
                <DataTable data={plans} columns={planColumns} />
              </TabsContent>

              <TabsContent value="tasks" className="pt-4 space-y-3">
                {MOCK_TASKS.map((task) => (
                  <motion.div key={task.id} variants={itemVariants} className="rounded-lg border p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${
                          task.status === "completed" ? "bg-green-100 text-green-700" :
                          task.status === "running" ? "bg-blue-100 text-blue-700" :
                          "bg-gray-100 text-gray-700"
                        }`}>
                          {task.id.toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{task.title}</p>
                          <p className="text-xs text-muted-foreground">{task.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Timer className="h-3 w-3" />{task.effort}h</span>
                        <span className="flex items-center gap-1"><UserCheck className="h-3 w-3" />{task.assignedAgent}</span>
                        <StatusDot status={task.status as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          <Settings className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                    {task.deps.length > 0 && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground border-t pt-2">
                        <GitBranch className="h-3 w-3" />
                        <span>Depends on: {task.deps.join(", ")}</span>
                      </div>
                    )}
                  </motion.div>
                ))}
              </TabsContent>

              <TabsContent value="graph" className="pt-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex flex-col items-center gap-4">
                      {[
                        { level: "Level 1", tasks: ["Gather Requirements"] },
                        { level: "Level 2", tasks: ["Design Architecture", "Design Database Schema"] },
                        { level: "Level 3", tasks: ["Develop Backend API", "Develop Frontend UI"] },
                      ].map((level, li) => (
                        <div key={level.level} className="flex flex-col items-center gap-2 w-full">
                          <span className="text-xs font-medium text-muted-foreground">{level.level}</span>
                          <div className="flex gap-3 flex-wrap justify-center">
                            {level.tasks.map((task) => (
                              <div key={task} className="flex items-center gap-2 rounded-md border bg-card px-4 py-2 text-sm shadow-sm">
                                <div className="h-2.5 w-2.5 rounded-full bg-primary" />
                                {task}
                              </div>
                            ))}
                          </div>
                          {li < 2 && <Layers className="h-5 w-5 text-muted-foreground rotate-90" />}
                        </div>
                      ))}

                      <div className="mt-6 w-full border-t pt-4">
                        <p className="text-xs font-medium text-muted-foreground mb-2">Critical Path</p>
                        <div className="flex items-center gap-2 text-sm">
                          <Badge variant="secondary">Gather Requirements</Badge>
                          <span className="text-muted-foreground">→</span>
                          <Badge variant="secondary">Design Architecture</Badge>
                          <span className="text-muted-foreground">→</span>
                          <Badge variant="secondary">Develop Backend API</Badge>
                          <span className="text-muted-foreground">→</span>
                          <Badge variant="secondary">Testing</Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="agents" className="pt-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {["research", "engineering", "design", "testing"].map((agent) => (
                    <Card key={agent}>
                      <CardHeader className="pb-2">
                        <CardTitle className="flex items-center gap-2 text-sm">
                          <UserCheck className="h-4 w-4 text-primary" />
                          {agent}
                          <Badge variant="outline" className="ml-auto text-xs">3 tasks</Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-1.5">
                          {MOCK_TASKS.filter((t) => t.assignedAgent === agent).map((t) => (
                            <div key={t.id} className="flex items-center justify-between text-xs">
                              <span>{t.title}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-muted-foreground">{t.effort}h</span>
                                <StatusDot status={t.status as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="timeline" className="pt-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="relative space-y-0">
                      {[
                        { time: "0m", event: "Plan created", status: "done" },
                        { time: "5m", event: "Goal analyzed — category: application", status: "done" },
                        { time: "10m", event: "Tasks decomposed — 9 tasks created", status: "done" },
                        { time: "15m", event: "Agents assigned — 4 agents selected", status: "done" },
                        { time: "20m", event: "Execution started", status: "done" },
                        { time: "25m", event: "Gather Requirements completed", status: "done" },
                        { time: "35m", event: "Design Architecture completed", status: "done" },
                        { time: "45m", event: "Design Database Schema (running)", status: "active" },
                        { time: "1h+", event: "Develop Backend API (pending)", status: "pending" },
                      ].map((item, i) => (
                        <div key={i} className="flex items-start gap-3 pb-4 last:pb-0">
                          <div className="flex flex-col items-center">
                            <div className={`h-2.5 w-2.5 rounded-full mt-1.5 ${
                              item.status === "done" ? "bg-green-500" :
                              item.status === "active" ? "bg-blue-500 ring-2 ring-blue-300" :
                              "bg-gray-300"
                            }`} />
                            {i < 8 && <div className="w-px flex-1 bg-border mt-1" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className={`text-sm ${item.status === "active" ? "font-medium" : ""}`}>{item.event}</span>
                              <span className="text-xs text-muted-foreground shrink-0 ml-2">{item.time}</span>
                            </div>
                          </div>
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
    </div>
  );
}
