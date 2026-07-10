"use client";

import { useState, useEffect, useCallback } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
  Brain, Target, GitBranch, ListChecks, PlayCircle, BarChart3, TrendingUp,
  Cpu, Activity, BookOpen, Plus, Settings, Trash2, Square, CheckCircle2,
  XCircle, AlertTriangle, Clock, Zap, Layers, TextSearch, ArrowRight,
  PauseCircle, RefreshCw, FileJson, History, Lightbulb, GripVertical,
} from "lucide-react";
import { useAppStore } from "@/stores/app-store";

const API = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
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
    paused: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  };
  const c = colors[status] || colors.draft;
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${c}`}>{status.replace("_", " ")}</span>;
}

export default function StudioIntelligencePage() {
  const { stats } = useAppStore();
  const [description, setDescription] = useState("");
  const [advancedMode, setAdvancedMode] = useState(false);
  const [priority, setPriority] = useState("medium");
  const [policy, setPolicy] = useState("balanced");
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [goals, setGoals] = useState<Record<string, unknown>[]>([]);
  const [plans, setPlans] = useState<Record<string, unknown>[]>([]);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [learning, setLearning] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [activeTab, setActiveTab] = useState("workspace");

  const fetchData = useCallback(() => {
    setLoading(true);
    Promise.all([
      fetch(`${API}/intelligence/status`).then((r) => r.json()).then((d) => setStatus(d.data)).catch(() => {}),
      fetch(`${API}/intelligence/goals`).then((r) => r.json()).then((d) => setGoals(d.data || [])).catch(() => {}),
      fetch(`${API}/intelligence/plans`).then((r) => r.json()).then((d) => setPlans(d.data || [])).catch(() => {}),
      fetch(`${API}/intelligence/metrics`).then((r) => r.json()).then((d) => setMetrics(d.data || {})).catch(() => {}),
      fetch(`${API}/intelligence/learning`).then((r) => r.json()).then((d) => {
        const records = d.data || d.records || [];
        setLearning(records);
      }).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleExecute = async () => {
    if (!description.trim()) return;
    setExecuting(true);
    try {
      const body: Record<string, unknown> = { description, priority, policy };
      if (advancedMode) {
        body.advanced = true;
      }
      const res = await fetch(`${API}/intelligence/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
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

  const handleCancel = async (id: string) => {
    try {
      await fetch(`${API}/intelligence/goals/${id}/cancel`, { method: "POST" });
      fetchData();
    } catch (err) {
      console.error("Cancel failed:", err);
    }
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <PageHeader
        title="Intelligence Workspace"
        description="Goal definition, planning, execution monitoring, and post-learning"
      />

      <ScrollArea className="flex-1 p-6">
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="max-w-7xl mx-auto space-y-6">
          <motion.div variants={itemVariants}>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="workspace"><Cpu className="h-4 w-4 mr-1.5" /> Workspace</TabsTrigger>
                <TabsTrigger value="goals"><Target className="h-4 w-4 mr-1.5" /> Goals</TabsTrigger>
                <TabsTrigger value="plans"><GitBranch className="h-4 w-4 mr-1.5" /> Plans</TabsTrigger>
                <TabsTrigger value="learning"><Lightbulb className="h-4 w-4 mr-1.5" /> Learning</TabsTrigger>
                <TabsTrigger value="logs"><FileJson className="h-4 w-4 mr-1.5" /> Logs</TabsTrigger>
              </TabsList>

              <TabsContent value="workspace" className="space-y-6">
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Active Goals</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <p className="text-2xl font-bold">{status?.active_goals ?? 0}</p>
                        <Target className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Active Plans</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <p className="text-2xl font-bold">{status?.active_plans ?? 0}</p>
                        <GitBranch className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Total Executions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <p className="text-2xl font-bold">{metrics?.total_executions ?? 0}</p>
                        <PlayCircle className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs text-muted-foreground">Learning Records</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <p className="text-2xl font-bold">{status?.total_learned ?? 0}</p>
                        <Lightbulb className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Brain className="h-5 w-5 text-primary" />
                      Execute New Goal
                    </CardTitle>
                    <CardDescription>
                      Describe what you want JARVIS to achieve. The Intelligence Core will plan, execute, and learn.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      placeholder="e.g., Refactor the authentication module to use OAuth2.0, update all related tests, document the new flow, and deploy to staging"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="min-h-[100px]"
                    />

                    <div className="flex items-center gap-4 flex-wrap">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">Priority:</span>
                        {["low", "medium", "high", "critical"].map((p) => (
                          <Button
                            key={p}
                            variant={priority === p ? "default" : "outline"}
                            size="sm"
                            className="h-7 text-xs capitalize"
                            onClick={() => setPriority(p)}
                          >
                            {p}
                          </Button>
                        ))}
                      </div>
                      <Separator orientation="vertical" className="h-6" />
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">Policy:</span>
                        {["conservative", "balanced", "aggressive"].map((p) => (
                          <Button
                            key={p}
                            variant={policy === p ? "default" : "outline"}
                            size="sm"
                            className="h-7 text-xs capitalize"
                            onClick={() => setPolicy(p)}
                          >
                            {p}
                          </Button>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <Button onClick={handleExecute} disabled={executing || !description.trim()} className="gap-2">
                        {executing ? (
                          <RefreshCw className="h-4 w-4 animate-spin" />
                        ) : (
                          <PlayCircle className="h-4 w-4" />
                        )}
                        {executing ? "Executing..." : "Execute"}
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setAdvancedMode(!advancedMode)} className="gap-1.5">
                        <Settings className="h-3.5 w-3.5" />
                        Advanced
                      </Button>
                    </div>

                    {advancedMode && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="rounded-lg border p-3 space-y-2">
                        <p className="text-xs font-medium text-muted-foreground">Advanced Options</p>
                        <div className="grid grid-cols-3 gap-3">
                          <div>
                            <label className="text-xs text-muted-foreground">Max steps</label>
                            <Input type="number" defaultValue={10} className="h-8 text-xs mt-1" />
                          </div>
                          <div>
                            <label className="text-xs text-muted-foreground">Timeout (s)</label>
                            <Input type="number" defaultValue={300} className="h-8 text-xs mt-1" />
                          </div>
                          <div>
                            <label className="text-xs text-muted-foreground">Context depth</label>
                            <Input type="number" defaultValue={3} className="h-8 text-xs mt-1" />
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </CardContent>
                </Card>

                <div className="grid gap-4 lg:grid-cols-2">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Activity className="h-4 w-4 text-primary" />
                        Execution Stats
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center">
                          <CheckCircle2 className="h-5 w-5 mx-auto text-green-500 mb-1" />
                          <p className="text-lg font-bold">{metrics?.successful_executions ?? 0}</p>
                          <p className="text-[10px] text-muted-foreground">Success</p>
                        </div>
                        <div className="text-center">
                          <XCircle className="h-5 w-5 mx-auto text-red-500 mb-1" />
                          <p className="text-lg font-bold">{metrics?.failed_executions ?? 0}</p>
                          <p className="text-[10px] text-muted-foreground">Failed</p>
                        </div>
                        <div className="text-center">
                          <Clock className="h-5 w-5 mx-auto text-blue-500 mb-1" />
                          <p className="text-lg font-bold">{(metrics?.avg_duration_seconds as number ?? 0).toFixed(1)}s</p>
                          <p className="text-[10px] text-muted-foreground">Avg Duration</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <BookOpen className="h-4 w-4 text-primary" />
                        Cognitive State
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Policy</span>
                          <Badge variant="outline" className="capitalize text-[10px]">{(status?.policy as string) || "balanced"}</Badge>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Confidence threshold</span>
                          <span>{status?.confidence_threshold as number ?? 0.7}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Total learned</span>
                          <span>{status?.total_learned ?? 0}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="goals" className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-muted-foreground">{goals.length} total goals</p>
                  <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={fetchData}>
                    <RefreshCw className="h-3 w-3" /> Refresh
                  </Button>
                </div>
                {goals.length === 0 && !loading && (
                  <div className="text-center py-12 border rounded-lg">
                    <Target className="h-10 w-10 mx-auto text-muted-foreground/40 mb-2" />
                    <p className="text-xs text-muted-foreground">No goals yet. Execute a goal in the Workspace tab.</p>
                  </div>
                )}
                {goals.map((goal, i) => (
                  <motion.div key={goal.id as string} variants={itemVariants}>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <GripVertical className="h-4 w-4 text-muted-foreground/30 mt-1 shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-medium">{goal.description as string}</p>
                                  <StatusBadge status={goal.state as string} />
                                </div>
                                <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                  <Badge variant="secondary" className="text-[10px] capitalize">{(goal.priority as string)}</Badge>
                                  <span>Created: {new Date(goal.created_at as string).toLocaleString()}</span>
                                </div>
                              </div>
                              <div className="flex items-center gap-1 shrink-0">
                                <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => handleCancel(goal.id as string)}>
                                  <Square className="h-3.5 w-3.5 text-muted-foreground" />
                                </Button>
                                <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                                  <Trash2 className="h-3.5 w-3.5 text-muted-foreground" />
                                </Button>
                              </div>
                            </div>
                            {goal.objectives && (goal.objectives as unknown[]).length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {(goal.objectives as string[]).slice(0, 3).map((obj, oi) => (
                                  <Badge key={oi} variant="outline" className="text-[10px]">{obj}</Badge>
                                ))}
                                {(goal.objectives as unknown[]).length > 3 && (
                                  <Badge variant="outline" className="text-[10px]">+{(goal.objectives as unknown[]).length - 3} more</Badge>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </TabsContent>

              <TabsContent value="plans" className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-muted-foreground">{plans.length} total plans</p>
                  <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={fetchData}>
                    <RefreshCw className="h-3 w-3" /> Refresh
                  </Button>
                </div>
                {plans.length === 0 && !loading && (
                  <div className="text-center py-12 border rounded-lg">
                    <GitBranch className="h-10 w-10 mx-auto text-muted-foreground/40 mb-2" />
                    <p className="text-xs text-muted-foreground">No plans yet.</p>
                  </div>
                )}
                {plans.map((plan, i) => (
                  <motion.div key={plan.id as string} variants={itemVariants}>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-3 flex-1 min-w-0">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 shrink-0">
                              <ListChecks className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <p className="text-sm font-medium">{plan.goal_description as string}</p>
                              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                <StatusBadge status={plan.status as string} />
                                <span>{plan.task_count as number} tasks</span>
                                <span>{new Date(plan.created_at as string).toLocaleString()}</span>
                              </div>
                              {(plan.tasks as Record<string, unknown>[])?.length > 0 && (
                                <div className="mt-2 space-y-1">
                                  {(plan.tasks as Record<string, unknown>[]).slice(0, 4).map((task, ti) => (
                                    <div key={ti} className="flex items-center gap-2 text-xs">
                                      {task.status === "completed" ? (
                                        <CheckCircle2 className="h-3 w-3 text-green-500" />
                                      ) : task.status === "failed" ? (
                                        <XCircle className="h-3 w-3 text-red-500" />
                                      ) : task.status === "in_progress" ? (
                                        <RefreshCw className="h-3 w-3 animate-spin text-yellow-500" />
                                      ) : (
                                        <Clock className="h-3 w-3 text-muted-foreground" />
                                      )}
                                      <span className="text-muted-foreground">{task.name as string}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </TabsContent>

              <TabsContent value="learning" className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-muted-foreground">{learning.length} learning records</p>
                  <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={fetchData}>
                    <RefreshCw className="h-3 w-3" /> Refresh
                  </Button>
                </div>
                {learning.length === 0 && !loading && (
                  <div className="text-center py-12 border rounded-lg">
                    <Lightbulb className="h-10 w-10 mx-auto text-muted-foreground/40 mb-2" />
                    <p className="text-xs text-muted-foreground">No learning records yet. The Intelligence Core learns from execution outcomes.</p>
                  </div>
                )}
                {learning.map((record, i) => (
                  <motion.div key={record.id as string || i} variants={itemVariants}>
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30 shrink-0">
                            <Lightbulb className={`h-4 w-4 ${record.outcome === "success" ? "text-green-600" : record.outcome === "failure" ? "text-red-600" : "text-yellow-600"}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-medium">{record.goal as string || "Learning record"}</p>
                              <Badge variant="outline" className={`text-[10px] capitalize ${record.outcome === "success" ? "text-green-600 border-green-200" : "text-red-600 border-red-200"}`}>
                                {record.outcome as string}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                              {(record.strategy as string) && `Strategy applied: ${record.strategy as string}`}
                              {(record.insight as string) && ` - ${record.insight as string}`}
                            </p>
                            {record.updated_at && (
                              <p className="text-[10px] text-muted-foreground mt-1">{new Date(record.updated_at as string).toLocaleString()}</p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </TabsContent>

              <TabsContent value="logs" className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-muted-foreground">Execution log (last 50 entries)</p>
                  <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={fetchData}>
                    <RefreshCw className="h-3 w-3" /> Refresh
                  </Button>
                </div>
                <Card>
                  <CardContent className="p-4">
                    <pre className="text-xs text-muted-foreground font-mono leading-relaxed">
                      {`[${new Date().toISOString()}] INFO  Intelligence Core initialized
[${new Date().toISOString()}] INFO  Gateway routes registered
[${new Date().toISOString()}] INFO  Ready to accept goals`}
                    </pre>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </motion.div>
        </motion.div>
      </ScrollArea>
    </div>
  );
}
