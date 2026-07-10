"use client";

import { useState, useEffect } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
  Brain,
  Target,
  GitBranch,
  ListChecks,
  Timer,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  PlayCircle,
  BarChart3,
  TrendingUp,
  Layers,
  Cpu,
  Zap,
  Activity,
  BookOpen,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    active: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    in_progress: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
    completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
    cancelled: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  };
  const c = colors[status] || colors.draft;
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${c}`}>{status.replace("_", " ")}</span>;
}

export default function IntelligencePage() {
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [goals, setGoals] = useState<Record<string, unknown>[]>([]);
  const [plans, setPlans] = useState<Record<string, unknown>[]>([]);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [executing, setExecuting] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      fetch(`${API}/intelligence/status`).then((r) => r.json()).then((d) => setStatus(d.data)).catch(() => {}),
      fetch(`${API}/intelligence/goals`).then((r) => r.json()).then((d) => setGoals(d.data || [])).catch(() => {}),
      fetch(`${API}/intelligence/plans`).then((r) => r.json()).then((d) => setPlans(d.data || [])).catch(() => {}),
      fetch(`${API}/intelligence/metrics`).then((r) => r.json()).then((d) => setMetrics(d.data || {})).catch(() => {}),
    ]).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleExecute = async () => {
    if (!description.trim()) return;
    setExecuting(true);
    try {
      const res = await fetch(`${API}/intelligence/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, priority: "medium", policy: "balanced" }),
      });
      const data = await res.json();
      if (data.ok) {
        fetchData();
        setDescription("");
      }
    } catch (err) {
      console.error("Execution failed:", err);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <PageHeader title="Intelligence Core" description="Central cognitive engine for goal planning and execution" />

      <ScrollArea className="flex-1 p-6">
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="max-w-6xl mx-auto space-y-6">
          <motion.div variants={itemVariants}>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="dashboard"><BarChart3 className="h-4 w-4 mr-1.5" /> Dashboard</TabsTrigger>
                <TabsTrigger value="goals"><Target className="h-4 w-4 mr-1.5" /> Goals</TabsTrigger>
                <TabsTrigger value="plans"><GitBranch className="h-4 w-4 mr-1.5" /> Plans</TabsTrigger>
                <TabsTrigger value="execute"><PlayCircle className="h-4 w-4 mr-1.5" /> Execute</TabsTrigger>
                <TabsTrigger value="metrics"><TrendingUp className="h-4 w-4 mr-1.5" /> Metrics</TabsTrigger>
              </TabsList>

              <TabsContent value="dashboard" className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-muted-foreground">Active Goals</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{String(status?.active_goals ?? 0)}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-muted-foreground">Active Plans</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{String(status?.active_plans ?? 0)}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-muted-foreground">Total Executions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{String(metrics?.total_executions ?? 0)}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-muted-foreground">Policy</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge variant="outline" className="capitalize">{(status?.policy as string) || "balanced"}</Badge>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-primary" />
                      Execution Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-6">
                      <div className="text-center">
                        <p className="text-3xl font-bold text-green-600">{String(metrics?.successful_executions ?? 0)}</p>
                        <p className="text-xs text-muted-foreground mt-1">Successful</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold text-red-600">{String(metrics?.failed_executions ?? 0)}</p>
                        <p className="text-xs text-muted-foreground mt-1">Failed</p>
                      </div>
                      <div className="text-center">
                        <p className="text-3xl font-bold">{(Number(metrics?.avg_duration_seconds) || 0).toFixed(1)}s</p>
                        <p className="text-xs text-muted-foreground mt-1">Avg Duration</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BookOpen className="h-5 w-5 text-primary" />
                      Learning Records
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{String(status?.total_learned ?? 0)}</p>
                    <p className="text-xs text-muted-foreground mt-1">Successful strategies stored in memory</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="goals" className="space-y-3">
                {goals.length === 0 && !loading && (
                  <div className="text-center py-12">
                    <Target className="h-12 w-12 mx-auto text-muted-foreground/40 mb-3" />
                    <p className="text-sm text-muted-foreground">No goals yet. Execute a goal to get started.</p>
                  </div>
                )}
                {goals.map((goal, i) => (
                  <motion.div key={goal.id as string} variants={itemVariants}>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-3 flex-1 min-w-0">
                            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 shrink-0">
                              <Target className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <p className="text-sm font-medium">{goal.description as string}</p>
                                <StatusBadge status={goal.state as string} />
                              </div>
                              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                <Badge variant="secondary" className="text-[10px] capitalize">{(goal.priority as string)}</Badge>
                                <span>Created: {new Date(goal.created_at as string).toLocaleDateString()}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </TabsContent>

              <TabsContent value="plans" className="space-y-3">
                {plans.length === 0 && !loading && (
                  <div className="text-center py-12">
                    <GitBranch className="h-12 w-12 mx-auto text-muted-foreground/40 mb-3" />
                    <p className="text-sm text-muted-foreground">No plans available.</p>
                  </div>
                )}
                {plans.map((plan, i) => (
                  <motion.div key={plan.id as string} variants={itemVariants}>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-3 flex-1 min-w-0">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 shrink-0">
                              <GitBranch className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <p className="text-sm font-medium">{plan.goal_description as string}</p>
                              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                <Badge variant="secondary" className="text-[10px]">{plan.status as string}</Badge>
                                <span>{plan.task_count as number} tasks</span>
                                <span>{new Date(plan.created_at as string).toLocaleDateString()}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </TabsContent>

              <TabsContent value="execute" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5 text-primary" />
                      Execute a Goal
                    </CardTitle>
                    <CardDescription>
                      Describe what you want JARVIS to achieve. The Intelligence Core will analyze, plan, and execute.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      placeholder="e.g., Design, build, test, document, and deploy a complete inventory management platform"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="h-11"
                    />
                    <Button onClick={handleExecute} disabled={executing || !description.trim()} className="gap-2">
                      {executing ? (
                        <Cpu className="h-4 w-4 animate-pulse" />
                      ) : (
                        <PlayCircle className="h-4 w-4" />
                      )}
                      {executing ? "Executing..." : "Execute Goal"}
                    </Button>
                  </CardContent>
                </Card>

                {metrics && (metrics.total_executions as number) > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Last Execution Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <CheckCircle2 className="h-5 w-5 mx-auto text-green-500 mb-1" />
                          <p className="text-lg font-bold">{metrics.successful_executions as number}</p>
                          <p className="text-xs text-muted-foreground">Successful</p>
                        </div>
                        <div>
                          <XCircle className="h-5 w-5 mx-auto text-red-500 mb-1" />
                          <p className="text-lg font-bold">{metrics.failed_executions as number}</p>
                          <p className="text-xs text-muted-foreground">Failed</p>
                        </div>
                        <div>
                          <BarChart3 className="h-5 w-5 mx-auto text-blue-500 mb-1" />
                          <p className="text-lg font-bold">{(Number(metrics.avg_duration_seconds) || 0).toFixed(1)}s</p>
                          <p className="text-xs text-muted-foreground">Avg Duration</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="metrics" className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-3">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Tasks Completed</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{String(metrics?.tasks_completed ?? 0)}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Tasks Failed</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-red-600">{String(metrics?.tasks_failed ?? 0)}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Decisions Made</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold">{String(metrics?.decisions_made ?? 0)}</p>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </motion.div>
        </motion.div>
      </ScrollArea>
    </div>
  );
}
