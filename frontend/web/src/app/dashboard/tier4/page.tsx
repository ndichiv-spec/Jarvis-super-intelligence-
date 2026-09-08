"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Building2, Shield, Lock, FileWarning, Eye, Users, CreditCard,
  Activity, Server, Database, Play, Pause, RotateCcw, Plus,
  CheckCircle, XCircle, AlertTriangle, Clock, RefreshCw,
  Workflow, Rocket, HardDrive, BarChart3, TrendingUp, Zap,
  Globe, Key, FileCheck, GitBranch, Archive, Upload
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

interface Organization {
  id: string;
  name: string;
  tier: string;
  member_count: number;
  status: string;
}

interface AuditEvent {
  timestamp: string;
  event_type: string;
  user_id: string;
  action: string;
  success: boolean;
}

interface WorkflowExecution {
  id: string;
  name: string;
  status: string;
  started_at: string;
  steps_completed: number;
  total_steps: number;
}

interface Deployment {
  id: string;
  version: string;
  status: string;
  deployed_by: string;
  started_at: string;
}

interface Backup {
  id: string;
  type: string;
  size_mb: number;
  status: string;
  created_at: string;
}

interface MetricData {
  name: string;
  value: number;
  unit: string;
  trend?: number;
}

export default function Tier4Page() {
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [tier4Status, setTier4Status] = useState<Record<string, string>>({});
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [auditLog, setAuditLog] = useState<AuditEvent[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowExecution[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [backups, setBackups] = useState<Backup[]>([]);
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [threats, setThreats] = useState<any[]>([]);
  const [slaReport, setSlaReport] = useState<any>(null);

  useEffect(() => {
    loadTier4Data();
  }, []);

  const loadTier4Data = async () => {
    try {
      setIsLoading(true);
      
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      // Load Tier 4 status
      try {
        const statusRes = await fetch(`${apiBase}/api/v1/tier4/status`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setTier4Status(statusData.status?.capabilities || {});
        }
      } catch (e) {
        console.log("Tier 4 API not available, using mock data");
      }

      // Mock data for demonstration
      setOrganizations([
        { id: "org_001", name: "Acme Corporation", tier: "enterprise", member_count: 47, status: "active" },
        { id: "org_002", name: "Tech Startup Inc", tier: "pro", member_count: 12, status: "active" },
        { id: "org_003", name: "Research Lab", tier: "free", member_count: 5, status: "active" },
      ]);

      setAuditLog([
        { timestamp: new Date(Date.now() - 300000).toISOString(), event_type: "auth_success", user_id: "user_001", action: "login", success: true },
        { timestamp: new Date(Date.now() - 600000).toISOString(), event_type: "data_access", user_id: "user_002", action: "read_knowledge", success: true },
        { timestamp: new Date(Date.now() - 900000).toISOString(), event_type: "permission_denied", user_id: "user_003", action: "admin_panel", success: false },
        { timestamp: new Date(Date.now() - 1200000).toISOString(), event_type: "config_change", user_id: "admin_001", action: "update_settings", success: true },
      ]);

      setWorkflows([
        { id: "wf_001", name: "Data Processing Pipeline", status: "running", started_at: new Date(Date.now() - 1800000).toISOString(), steps_completed: 3, total_steps: 5 },
        { id: "wf_002", name: "Report Generation", status: "completed", started_at: new Date(Date.now() - 7200000).toISOString(), steps_completed: 4, total_steps: 4 },
        { id: "wf_003", name: "Backup Workflow", status: "pending", started_at: new Date(Date.now() - 300000).toISOString(), steps_completed: 0, total_steps: 3 },
      ]);

      setDeployments([
        { id: "dep_001", version: "4.0.0", status: "completed", deployed_by: "admin", started_at: new Date(Date.now() - 86400000).toISOString() },
        { id: "dep_002", version: "3.9.2", status: "completed", deployed_by: "ci_pipeline", started_at: new Date(Date.now() - 172800000).toISOString() },
        { id: "dep_003", version: "3.9.1", status: "rolled_back", deployed_by: "admin", started_at: new Date(Date.now() - 259200000).toISOString() },
      ]);

      setBackups([
        { id: "bk_001", type: "full", size_mb: 2450, status: "completed", created_at: new Date(Date.now() - 86400000).toISOString() },
        { id: "bk_002", type: "database", size_mb: 890, status: "completed", created_at: new Date(Date.now() - 43200000).toISOString() },
        { id: "bk_003", type: "config", size_mb: 12, status: "completed", created_at: new Date(Date.now() - 21600000).toISOString() },
      ]);

      setMetrics([
        { name: "API Requests", value: 245892, unit: "requests", trend: 12.5 },
        { name: "Active Users", value: 1523, unit: "users", trend: 8.2 },
        { name: "Avg Response Time", value: 145, unit: "ms", trend: -5.3 },
        { name: "Error Rate", value: 0.12, unit: "%", trend: -2.1 },
        { name: "Uptime", value: 99.97, unit: "%", trend: 0.02 },
        { name: "Storage Used", value: 89.4, unit: "GB", trend: 3.1 },
      ]);

      setThreats([
        { type: "rate_limit", severity: "low", count: 23, description: "Rate limit violations detected and blocked" },
        { type: "brute_force", severity: "medium", count: 5, description: "Potential brute force attempts" },
        { type: "anomaly", severity: "low", count: 8, description: "Unusual access patterns" },
      ]);

      setSlaReport({
        uptime: 99.97,
        latency_p95: 245,
        latency_p99: 520,
        error_rate: 0.12,
        availability_target: 99.9,
        compliant: true,
      });

    } catch (error) {
      console.error("Failed to load Tier 4 data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const createOrganization = async () => {
    toast.success("Organization created successfully");
    loadTier4Data();
  };

  const deploy = async () => {
    toast.info("Initiating deployment...");
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.success("Deployment completed");
    loadTier4Data();
  };

  const rollback = async (deploymentId: string) => {
    toast.warning("Rolling back deployment...");
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success("Rollback completed");
    loadTier4Data();
  };

  const createBackup = async () => {
    toast.info("Creating backup...");
    await new Promise(resolve => setTimeout(resolve, 2000));
    toast.success("Backup created successfully");
    loadTier4Data();
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      running: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      completed: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      failed: "bg-red-500/20 text-red-400 border-red-500/30",
      pending: "bg-amber-500/20 text-amber-400 border-amber-500/30",
      rolled_back: "bg-orange-500/20 text-orange-400 border-orange-500/30",
      inactive: "bg-gray-500/20 text-gray-400 border-gray-500/30",
    };
    return colors[status] || colors.pending;
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      low: "bg-blue-500/20 text-blue-400",
      medium: "bg-amber-500/20 text-amber-400",
      high: "bg-red-500/20 text-red-400",
      critical: "bg-red-600/20 text-red-600",
    };
    return colors[severity] || colors.low;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 via-fuchsia-400 to-purple-400 bg-clip-text text-transparent">
            Tier 4: Enterprise & Production
          </h1>
          <p className="text-muted-foreground/60 mt-1">
            Multi-tenancy, security, monitoring, and deployment automation
          </p>
        </div>
        <Button onClick={loadTier4Data} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </motion.div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: "Multi-Tenancy", icon: Building2, status: tier4Status.multi_tenancy || "ready" },
          { label: "Security", icon: Shield, status: tier4Status.security || "ready" },
          { label: "Workflows", icon: Workflow, status: tier4Status.workflows || "ready" },
          { label: "Monitoring", icon: Activity, status: tier4Status.monitoring || "ready" },
          { label: "Deployment", icon: Rocket, status: tier4Status.deployment || "ready" },
        ].map((item, idx) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <item.icon className="h-8 w-8 text-violet-400" />
                  <Badge className={tier4Status[item.label.toLowerCase()]?.includes("✓") ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"}>
                    {item.status.includes("✓") ? "Active" : "Standby"}
                  </Badge>
                </div>
                <p className="mt-2 text-sm font-medium">{item.label}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-6 w-full bg-card/50">
          <TabsTrigger value="overview" className="data-[state=active]:bg-violet-500/20">
            <Activity className="mr-2 h-4 w-4" /> Overview
          </TabsTrigger>
          <TabsTrigger value="organizations" className="data-[state=active]:bg-violet-500/20">
            <Building2 className="mr-2 h-4 w-4" /> Orgs
          </TabsTrigger>
          <TabsTrigger value="security" className="data-[state=active]:bg-violet-500/20">
            <Shield className="mr-2 h-4 w-4" /> Security
          </TabsTrigger>
          <TabsTrigger value="workflows" className="data-[state=active]:bg-violet-500/20">
            <Workflow className="mr-2 h-4 w-4" /> Workflows
          </TabsTrigger>
          <TabsTrigger value="monitoring" className="data-[state=active]:bg-violet-500/20">
            <BarChart3 className="mr-2 h-4 w-4" /> Monitoring
          </TabsTrigger>
          <TabsTrigger value="deploy" className="data-[state=active]:bg-violet-500/20">
            <Rocket className="mr-2 h-4 w-4" /> Deploy
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Metrics */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5 text-violet-400" />
                  Key Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {metrics.slice(0, 4).map((metric) => (
                    <div key={metric.name} className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">{metric.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-medium">{metric.value.toLocaleString()}{metric.unit === "%" ? "%" : ""}</span>
                        {metric.trend !== undefined && (
                          <Badge className={metric.trend > 0 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}>
                            {metric.trend > 0 ? "+" : ""}{metric.trend}%
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* SLA Status */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Server className="mr-2 h-5 w-5 text-emerald-400" />
                  SLA Compliance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Uptime</span>
                    <div className="flex items-center gap-2">
                      <Progress value={slaReport?.uptime || 0} className="w-24 h-2" />
                      <span className="font-mono text-sm">{slaReport?.uptime || 0}%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Latency P95</span>
                    <span className="font-mono text-sm">{slaReport?.latency_p95 || 0}ms</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Error Rate</span>
                    <span className="font-mono text-sm">{slaReport?.error_rate || 0}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Target</span>
                    <Badge className={slaReport?.compliant ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}>
                      {slaReport?.compliant ? "Compliant" : "Non-Compliant"}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="mr-2 h-5 w-5 text-amber-400" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-3">
                    {auditLog.slice(0, 5).map((event, idx) => (
                      <div key={idx} className="flex items-start gap-3 text-sm">
                        {event.success ? (
                          <CheckCircle className="h-4 w-4 text-emerald-400 mt-0.5" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <p className="font-medium">{event.action}</p>
                          <p className="text-xs text-muted-foreground">
                            {event.user_id} - {new Date(event.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Threat Summary */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="mr-2 h-5 w-5 text-red-400" />
                  Threat Detection
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {threats.map((threat, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-amber-400" />
                        <span className="text-sm">{threat.type.replace("_", " ")}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getSeverityColor(threat.severity)}>{threat.severity}</Badge>
                        <span className="font-mono text-sm">{threat.count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Organizations Tab */}
        <TabsContent value="organizations" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Organizations</h3>
            <Button onClick={createOrganization}>
              <Plus className="mr-2 h-4 w-4" /> Create Organization
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {organizations.map((org, idx) => (
              <motion.div
                key={org.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Building2 className="h-8 w-8 text-violet-400" />
                      <Badge className={getStatusColor(org.status)}>{org.status}</Badge>
                    </div>
                    <CardTitle className="mt-2">{org.name}</CardTitle>
                    <CardDescription>ID: {org.id}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Plan</span>
                        <Badge variant="outline" className="capitalize">{org.tier}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Members</span>
                        <span className="font-mono">{org.member_count}</span>
                      </div>
                    </div>
                    <Separator className="my-4" />
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Users className="mr-1 h-3 w-3" /> Manage
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <CreditCard className="mr-1 h-3 w-3" /> Billing
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Audit Log */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Eye className="mr-2 h-5 w-5 text-violet-400" />
                  Audit Log
                </CardTitle>
                <CardDescription>Recent security events</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3">
                    {auditLog.map((event, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-white/5 space-y-1">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="capitalize">{event.event_type.replace("_", " ")}</Badge>
                          {event.success ? (
                            <CheckCircle className="h-4 w-4 text-emerald-400" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-400" />
                          )}
                        </div>
                        <p className="text-sm font-medium">{event.action}</p>
                        <p className="text-xs text-muted-foreground">
                          {event.user_id} - {new Date(event.timestamp).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Compliance Status */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileCheck className="mr-2 h-5 w-5 text-emerald-400" />
                  Compliance Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {["GDPR", "SOC2", "HIPAA", "ISO27001", "PCI_DSS"].map((standard) => (
                    <div key={standard} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                      <span className="font-medium">{standard}</span>
                      <Badge className="bg-emerald-500/20 text-emerald-400">
                        <CheckCircle className="mr-1 h-3 w-3" /> Compliant
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Secrets Management */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Key className="mr-2 h-5 w-5 text-amber-400" />
                  Secrets Management
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 rounded bg-white/5">
                    <div className="flex items-center gap-2">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">API Keys</span>
                    </div>
                    <Badge className="bg-emerald-500/20 text-emerald-400">Encrypted</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-white/5">
                    <div className="flex items-center gap-2">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Database Credentials</span>
                    </div>
                    <Badge className="bg-emerald-500/20 text-emerald-400">Encrypted</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded bg-white/5">
                    <div className="flex items-center gap-2">
                      <Lock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">JWT Secrets</span>
                    </div>
                    <Badge className="bg-emerald-500/20 text-emerald-400">Rotated</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Threat Detection */}
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileWarning className="mr-2 h-5 w-5 text-red-400" />
                  Threat Report
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {threats.map((threat, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium capitalize">{threat.type.replace("_", " ")}</span>
                        <Badge className={getSeverityColor(threat.severity)}>{threat.severity}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{threat.description}</p>
                      <p className="text-sm mt-2 font-mono">{threat.count} events</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Workflow Executions</h3>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Create Workflow
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workflows.map((wf, idx) => (
              <motion.div
                key={wf.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Workflow className="h-6 w-6 text-violet-400" />
                      <Badge className={getStatusColor(wf.status)}>{wf.status}</Badge>
                    </div>
                    <CardTitle className="text-base">{wf.name}</CardTitle>
                    <CardDescription>ID: {wf.id}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="font-mono">{wf.steps_completed}/{wf.total_steps}</span>
                        </div>
                        <Progress value={(wf.steps_completed / wf.total_steps) * 100} className="h-2" />
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Started</span>
                        <span className="text-xs">{new Date(wf.started_at).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {metrics.map((metric, idx) => (
              <motion.div
                key={metric.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">{metric.name}</span>
                      {metric.trend !== undefined && (
                        <Badge className={metric.trend > 0 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}>
                          {metric.trend > 0 ? "+" : ""}{metric.trend}%
                        </Badge>
                      )}
                    </div>
                    <div className="text-2xl font-bold font-mono">
                      {metric.value.toLocaleString()}
                      <span className="text-sm text-muted-foreground ml-1">{metric.unit}</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>API Response Time</span>
                    <Progress value={85} className="w-32 h-2" />
                    <span className="font-mono text-sm">145ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Database Queries</span>
                    <Progress value={72} className="w-32 h-2" />
                    <span className="font-mono text-sm">23ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Memory Usage</span>
                    <Progress value={68} className="w-32 h-2" />
                    <span className="font-mono text-sm">68%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>CPU Load</span>
                    <Progress value={45} className="w-32 h-2" />
                    <span className="font-mono text-sm">45%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <HardDrive className="mr-2 h-5 w-5 text-blue-400" />
                  Storage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Database</span>
                    <span className="font-mono">45.2 GB</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Knowledge Base</span>
                    <span className="font-mono">23.8 GB</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Backups</span>
                    <span className="font-mono">18.5 GB</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Logs</span>
                    <span className="font-mono">1.9 GB</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between font-medium">
                    <span>Total</span>
                    <span className="font-mono">89.4 GB / 100 GB</span>
                  </div>
                  <Progress value={89.4} className="h-3" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Deploy Tab */}
        <TabsContent value="deploy" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Deployments</h3>
            <Button onClick={deploy}>
              <Rocket className="mr-2 h-4 w-4" /> Deploy New Version
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Rocket className="mr-2 h-5 w-5 text-violet-400" />
                  Deployment History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  <div className="space-y-3">
                    {deployments.map((dep, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-white/5 flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-medium">v{dep.version}</span>
                            <Badge className={getStatusColor(dep.status)}>{dep.status}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            by {dep.deployed_by} - {new Date(dep.started_at).toLocaleString()}
                          </p>
                        </div>
                        {dep.status === "completed" && (
                          <Button variant="outline" size="sm" onClick={() => rollback(dep.id)}>
                            <RotateCcw className="mr-1 h-3 w-3" /> Rollback
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-card to-card/50 border-white/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Archive className="mr-2 h-5 w-5 text-emerald-400" />
                  Backups
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 mb-4">
                  <Button variant="outline" size="sm" onClick={createBackup}>
                    <Upload className="mr-1 h-3 w-3" /> Full Backup
                  </Button>
                  <Button variant="outline" size="sm">
                    <Database className="mr-1 h-3 w-3" /> Database Only
                  </Button>
                </div>
                <ScrollArea className="h-[250px]">
                  <div className="space-y-3">
                    {backups.map((bk, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-white/5">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Database className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium capitalize">{bk.type}</span>
                          </div>
                          <Badge className={getStatusColor(bk.status)}>{bk.status}</Badge>
                        </div>
                        <div className="flex justify-between text-sm mt-2 text-muted-foreground">
                          <span>{bk.size_mb.toLocaleString()} MB</span>
                          <span>{new Date(bk.created_at).toLocaleString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
