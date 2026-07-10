"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  PauseCircle,
  UserCheck,
  FileText,
  TrendingUp,
  Layers,
} from "lucide-react";
import { motion } from "framer-motion";

interface PlanGoal {
  objective: string;
  category: string;
  complexity: string;
  estimated_duration: string;
  risk_level: string;
  confidence: number;
}

interface PlanTask {
  id: string;
  title: string;
  description: string;
  status: string;
  assigned_agent: string;
  estimated_effort_hours: number;
  dependencies: string[];
  group: string;
}

interface Plan {
  id: string;
  objective: string;
  status: string;
  goal: PlanGoal | null;
  tasks: PlanTask[];
  progress: {
    completion_percentage: number;
    completed_tasks: number;
    total_tasks: number;
    running_tasks: number;
    failed_tasks: number;
    active_task: string;
  } | null;
}

const MOCK_PLANS: Plan[] = [
  {
    id: "plan-1",
    objective: "Build a professional inventory management platform",
    status: "executing",
    goal: {
      objective: "Build a professional inventory management platform",
      category: "application",
      complexity: "complex",
      estimated_duration: "weeks",
      risk_level: "medium",
      confidence: 0.85,
    },
    tasks: [
      { id: "t1", title: "Gather Requirements", description: "Collect functional and non-functional requirements", status: "completed", assigned_agent: "research", estimated_effort_hours: 4.0, dependencies: [], group: "initiation" },
      { id: "t2", title: "Design Architecture", description: "Design system architecture", status: "completed", assigned_agent: "engineering", estimated_effort_hours: 6.0, dependencies: ["t1"], group: "design" },
      { id: "t3", title: "Design Database Schema", description: "Design database tables and relationships", status: "running", assigned_agent: "engineering", estimated_effort_hours: 4.0, dependencies: ["t1"], group: "design" },
      { id: "t4", title: "Develop Backend API", description: "Implement RESTful API services", status: "waiting", assigned_agent: "engineering", estimated_effort_hours: 12.0, dependencies: ["t2", "t3"], group: "development" },
      { id: "t5", title: "Develop Frontend UI", description: "Implement user interface", status: "waiting", assigned_agent: "design", estimated_effort_hours: 10.0, dependencies: ["t2"], group: "development" },
    ],
    progress: { completion_percentage: 35, completed_tasks: 2, total_tasks: 9, running_tasks: 1, failed_tasks: 0, active_task: "Design Database Schema" },
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, { label: string; class: string }> = {
    completed: { label: "Completed", class: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
    running: { label: "Running", class: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400" },
    waiting: { label: "Waiting", class: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400" },
    blocked: { label: "Blocked", class: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400" },
    planned: { label: "Planned", class: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400" },
  };
  const v = variants[status] || { label: status, class: "bg-gray-100 text-gray-800" };
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${v.class}`}>{v.label}</span>;
}

export default function PlanningPage() {
  const [objective, setObjective] = useState("");
  const [plans] = useState<Plan[]>(MOCK_PLANS);
  const [activeTab, setActiveTab] = useState("overview");

  const activePlan = plans[0];

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <PageHeader
        title="Planning Engine"
        description="Cognitive planning for complex objectives"
      />

      <ScrollArea className="flex-1 p-6">
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="max-w-5xl mx-auto space-y-6">
          <motion.div variants={itemVariants} className="flex gap-4">
            <Input
              placeholder="Enter a complex objective (e.g., Build an accounting platform...)"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="flex-1 h-11"
            />
            <Button className="h-11 gap-2">
              <Brain className="h-4 w-4" /> Create Plan
            </Button>
          </motion.div>

          {activePlan && activePlan.goal && (
            <>
              <motion.div variants={itemVariants}>
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Target className="h-5 w-5 text-primary" />
                      Current Goal
                    </CardTitle>
                    <CardDescription>{activePlan.goal.objective}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-3">
                      <Badge variant="secondary">{activePlan.goal.category}</Badge>
                      <Badge variant="secondary">{activePlan.goal.complexity}</Badge>
                      <Badge variant="secondary">{activePlan.goal.estimated_duration}</Badge>
                      <Badge variant={activePlan.goal.risk_level === "high" ? "destructive" : "secondary"}>
                        Risk: {activePlan.goal.risk_level}
                      </Badge>
                      <Badge variant="outline">Confidence: {(activePlan.goal.confidence * 100).toFixed(0)}%</Badge>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {activePlan.progress && (
                <motion.div variants={itemVariants}>
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <TrendingUp className="h-5 w-5 text-primary" />
                        Execution Progress
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Overall Completion</span>
                          <span className="font-medium">{activePlan.progress.completion_percentage}%</span>
                        </div>
                        <Progress value={activePlan.progress.completion_percentage} className="h-2" />
                        <div className="grid grid-cols-4 gap-4 pt-2">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">{activePlan.progress.completed_tasks}</p>
                            <p className="text-xs text-muted-foreground">Completed</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-blue-600">{activePlan.progress.running_tasks}</p>
                            <p className="text-xs text-muted-foreground">Running</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-red-600">{activePlan.progress.failed_tasks}</p>
                            <p className="text-xs text-muted-foreground">Failed</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold">{activePlan.progress.total_tasks}</p>
                            <p className="text-xs text-muted-foreground">Total Tasks</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              <motion.div variants={itemVariants}>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList>
                    <TabsTrigger value="overview">
                      <ListChecks className="h-4 w-4 mr-1.5" /> Task Tree
                    </TabsTrigger>
                    <TabsTrigger value="agents">
                      <UserCheck className="h-4 w-4 mr-1.5" /> Assigned Agents
                    </TabsTrigger>
                    <TabsTrigger value="graph">
                      <GitBranch className="h-4 w-4 mr-1.5" /> Dependency Graph
                    </TabsTrigger>
                    <TabsTrigger value="reasoning">
                      <Brain className="h-4 w-4 mr-1.5" /> Reasoning
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-3 pt-4">
                    {activePlan.tasks.map((task) => (
                      <motion.div key={task.id} variants={itemVariants} className="flex items-center gap-3 rounded-lg border p-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-xs font-medium">
                          {task.id.replace("task-", "T")}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{task.title}</span>
                            <StatusBadge status={task.status} />
                          </div>
                          <p className="text-xs text-muted-foreground truncate">{task.description}</p>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground shrink-0">
                          <Timer className="h-3 w-3" />
                          <span>{task.estimated_effort_hours}h</span>
                          {task.assigned_agent && (
                            <>
                              <UserCheck className="h-3 w-3 ml-2" />
                              <span>{task.assigned_agent}</span>
                            </>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </TabsContent>

                  <TabsContent value="agents" className="pt-4">
                    <div className="grid gap-3">
                      {Array.from(new Set(activePlan.tasks.map((t) => t.assigned_agent))).map((agent) => (
                        <Card key={agent}>
                          <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-sm">
                              <UserCheck className="h-4 w-4 text-primary" />
                              {agent}
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-1">
                              {activePlan.tasks.filter((t) => t.assigned_agent === agent).map((t) => (
                                <div key={t.id} className="flex items-center justify-between text-xs">
                                  <span>{t.title}</span>
                                  <StatusBadge status={t.status} />
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="graph" className="pt-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="flex flex-col items-center gap-3">
                          {["Level 1", "Level 2", "Level 3"].map((level, li) => (
                            <div key={level} className="flex flex-col items-center gap-2 w-full">
                              <span className="text-xs font-medium text-muted-foreground">{level}</span>
                              <div className="flex gap-2 flex-wrap justify-center">
                                {activePlan.tasks
                                  .filter((_, ti) => {
                                    if (li === 0) return ti < 2;
                                    if (li === 1) return ti >= 2 && ti < 4;
                                    return ti >= 4;
                                  })
                                  .map((t) => (
                                    <div key={t.id} className="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs">
                                      <div className={`h-2 w-2 rounded-full ${
                                        t.status === "completed" ? "bg-green-500" :
                                        t.status === "running" ? "bg-blue-500" :
                                        t.status === "blocked" ? "bg-red-500" : "bg-gray-300"
                                      }`} />
                                      {t.title}
                                    </div>
                                  ))}
                              </div>
                              {li < 2 && <Layers className="h-4 w-4 text-muted-foreground rotate-90" />}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="reasoning" className="pt-4 space-y-3">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Why This Plan Exists</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">
                          The objective &ldquo;{activePlan.goal.objective}&rdquo; was analyzed as a {activePlan.goal.complexity} {activePlan.goal.category} project.
                          It requires expertise in software architecture, backend development, and database design.
                        </p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Why Tasks Are Ordered This Way</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">
                          Requirements must be gathered first (no dependencies). Architecture and database design
                          depend on requirements. Backend and frontend development depend on architecture approval.
                          This ensures work is built on a validated foundation.
                        </p>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </motion.div>
            </>
          )}

          {!activePlan && (
            <motion.div variants={itemVariants} className="text-center py-20">
              <Brain className="h-16 w-16 mx-auto text-muted-foreground/40 mb-4" />
              <h3 className="text-lg font-medium mb-2">No Active Plan</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Enter an objective above and JARVIS will analyze, decompose, and create an execution plan with task dependencies, agent assignments, and progress tracking.
              </p>
            </motion.div>
          )}
        </motion.div>
      </ScrollArea>
    </div>
  );
}
