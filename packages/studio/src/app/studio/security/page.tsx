"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { DataTable } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  Shield, Users, Key, FileText, Activity, Fingerprint,
  CheckCircle2, XCircle,
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

type UserStatus = "active" | "inactive" | "suspended";

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: UserStatus;
  lastActive: string;
  mfaEnabled: boolean;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissionsCount: number;
  userCount: number;
}

interface Policy {
  id: string;
  name: string;
  description: string;
  rulesCount: number;
  enabled: boolean;
}

interface AuditEntry {
  id: string;
  actor: string;
  action: string;
  resource: string;
  details: string;
  ip: string;
  timestamp: string;
}

const users: User[] = [
  { id: "u1", name: "Alex Morgan", email: "alex@jarvis.io", role: "Admin", status: "active", lastActive: "2 min ago", mfaEnabled: true },
  { id: "u2", name: "Sarah Chen", email: "sarah@jarvis.io", role: "Engineer", status: "active", lastActive: "15 min ago", mfaEnabled: true },
  { id: "u3", name: "Marcus Webb", email: "marcus@jarvis.io", role: "Viewer", status: "inactive", lastActive: "3 days ago", mfaEnabled: false },
  { id: "u4", name: "Priya Patel", email: "priya@jarvis.io", role: "Admin", status: "active", lastActive: "1 hour ago", mfaEnabled: true },
  { id: "u5", name: "James Liu", email: "james@jarvis.io", role: "Engineer", status: "suspended", lastActive: "1 week ago", mfaEnabled: false },
  { id: "u6", name: "Emma Wilson", email: "emma@jarvis.io", role: "Engineer", status: "active", lastActive: "5 min ago", mfaEnabled: true },
  { id: "u7", name: "David Kim", email: "david@jarvis.io", role: "Viewer", status: "active", lastActive: "1 day ago", mfaEnabled: false },
  { id: "u8", name: "Olivia Brown", email: "olivia@jarvis.io", role: "Admin", status: "inactive", lastActive: "2 weeks ago", mfaEnabled: true },
];

const roles: Role[] = [
  { id: "r1", name: "Admin", description: "Full system access with all permissions", permissionsCount: 47, userCount: 3 },
  { id: "r2", name: "Engineer", description: "Can manage agents, workflows, and tools", permissionsCount: 28, userCount: 3 },
  { id: "r3", name: "Viewer", description: "Read-only access to dashboards and logs", permissionsCount: 12, userCount: 2 },
  { id: "r4", name: "Auditor", description: "Access to audit logs and compliance reports", permissionsCount: 18, userCount: 0 },
];

const policies: Policy[] = [
  { id: "p1", name: "Password Policy", description: "Minimum length, complexity, and rotation rules", rulesCount: 6, enabled: true },
  { id: "p2", name: "Session Policy", description: "Idle timeout, max concurrent sessions, and IP restrictions", rulesCount: 4, enabled: true },
  { id: "p3", name: "API Rate Limit", description: "Throttling rules for API endpoints per role", rulesCount: 8, enabled: false },
];

const auditLogs: AuditEntry[] = [
  { id: "a1", actor: "Alex Morgan", action: "user.login", resource: "Session", details: "Login from trusted device", ip: "192.168.1.42", timestamp: "2026-06-30 09:15:23" },
  { id: "a2", actor: "Sarah Chen", action: "agent.create", resource: "CodeAssistant v2", details: "Created new agent from template", ip: "10.0.0.85", timestamp: "2026-06-30 09:12:01" },
  { id: "a3", actor: "System", action: "policy.enforce", resource: "Password Policy", details: "Rotation reminder sent to 3 users", ip: "127.0.0.1", timestamp: "2026-06-30 08:00:00" },
  { id: "a4", actor: "Priya Patel", action: "role.update", resource: "Engineer", details: "Added workflow:write permission", ip: "192.168.1.55", timestamp: "2026-06-29 17:45:33" },
  { id: "a5", actor: "James Liu", action: "user.logout", resource: "Session", details: "Session terminated by admin", ip: "10.0.0.12", timestamp: "2026-06-29 16:30:12" },
  { id: "a6", actor: "Emma Wilson", action: "secret.access", resource: "Vault: api-key-prod", details: "Decrypted secret for workflow execution", ip: "10.0.0.85", timestamp: "2026-06-29 15:22:44" },
  { id: "a7", actor: "System", action: "scan.complete", resource: "Security Scan", details: "Vulnerability scan completed: 0 critical, 2 high", ip: "127.0.0.1", timestamp: "2026-06-29 14:00:00" },
  { id: "a8", actor: "David Kim", action: "dashboard.view", resource: "Analytics", details: "Exported monthly usage report", ip: "203.0.113.45", timestamp: "2026-06-29 11:08:19" },
  { id: "a9", actor: "Olivia Brown", action: "policy.create", resource: "API Rate Limit", details: "Draft policy created for review", ip: "192.168.1.100", timestamp: "2026-06-28 22:14:55" },
  { id: "a10", actor: "Alex Morgan", action: "user.invite", resource: "Invitation", details: "Invited 2 new engineers to the platform", ip: "192.168.1.42", timestamp: "2026-06-28 10:00:00" },
];

const activeSessions = 24;

export default function SecurityCenterPage() {
  const { data: usersData } = useData(() => api.security.users());
  const { data: rolesData } = useData(() => api.security.roles());
  const { data: policiesData } = useData(() => api.security.policies());
  const { data: auditData } = useData(() => api.security.auditLog());
  const userList = (usersData || users) as User[];
  const roleList = (rolesData || roles) as Role[];
  const policyList = (policiesData || policies) as Policy[];
  const auditList = (auditData || auditLogs) as AuditEntry[];
  return (
    <div className="pb-8">
      <PageHeader
        title="Security Center"
        description="Manage users, roles, permissions, and audit logs"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Users" value={userList.length} icon={Users} trend={{ value: 2, positive: true }} />
          <StatCard title="Active Sessions" value={activeSessions} icon={Activity} />
          <StatCard title="Roles" value={roleList.length} icon={Key} />
          <StatCard title="Security Policies" value={policyList.filter(p => p.enabled).length} icon={Shield} description={`${policyList.length} total`} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="users">
            <TabsList>
              <TabsTrigger value="users">Users</TabsTrigger>
              <TabsTrigger value="roles">Roles</TabsTrigger>
              <TabsTrigger value="policies">Policies</TabsTrigger>
              <TabsTrigger value="audit">Audit Log</TabsTrigger>
            </TabsList>

            <TabsContent value="users" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">User Management</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<User>
                    columns={[
                      {
                        key: "name",
                        header: "Name",
                        cell: (user) => (
                          <div className="flex items-center gap-2">
                            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10">
                              <span className="text-xs font-medium text-primary">
                                {user.name.split(" ").map(n => n[0]).join("")}
                              </span>
                            </div>
                            <span className="font-medium">{user.name}</span>
                          </div>
                        ),
                      },
                      {
                        key: "email",
                        header: "Email",
                        cell: (user) => (
                          <span className="text-xs text-muted-foreground">{user.email}</span>
                        ),
                      },
                      {
                        key: "role",
                        header: "Role",
                        cell: (user) => (
                          <Badge
                            variant={
                              user.role === "Admin" ? "default" :
                              user.role === "Engineer" ? "secondary" : "outline"
                            }
                            className="text-[10px]"
                          >
                            {user.role}
                          </Badge>
                        ),
                      },
                      {
                        key: "status",
                        header: "Status",
                        cell: (user) => (
                          <div className="flex items-center gap-1.5">
                            <StatusDot status={user.status} />
                            <span className="text-xs capitalize text-muted-foreground">{user.status}</span>
                          </div>
                        ),
                      },
                      {
                        key: "lastActive",
                        header: "Last Active",
                        cell: (user) => (
                          <span className="text-xs text-muted-foreground">{user.lastActive}</span>
                        ),
                      },
                      {
                        key: "mfaEnabled",
                        header: "MFA",
                        className: "text-center",
                        cell: (user) => (
                          user.mfaEnabled
                            ? <CheckCircle2 className="h-4 w-4 text-status-success mx-auto" />
                            : <XCircle className="h-4 w-4 text-muted-foreground mx-auto" />
                        ),
                      },
                    ]}
                    data={userList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="roles" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Role Management</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<Role>
                    columns={[
                      {
                        key: "name",
                        header: "Role",
                        cell: (role) => (
                          <div className="flex items-center gap-2">
                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                              <Key className="h-3.5 w-3.5 text-primary" />
                            </div>
                            <span className="font-medium">{role.name}</span>
                          </div>
                        ),
                      },
                      {
                        key: "description",
                        header: "Description",
                        cell: (role) => (
                          <span className="text-xs text-muted-foreground">{role.description}</span>
                        ),
                      },
                      {
                        key: "permissionsCount",
                        header: "Permissions",
                        className: "text-right",
                        cell: (role) => (
                          <span className="text-xs tabular-nums">{role.permissionsCount}</span>
                        ),
                      },
                      {
                        key: "userCount",
                        header: "Users",
                        className: "text-right",
                        cell: (role) => (
                          <span className="text-xs tabular-nums">{role.userCount}</span>
                        ),
                      },
                    ]}
                    data={roleList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="policies" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Security Policies</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<Policy>
                    columns={[
                      {
                        key: "name",
                        header: "Policy",
                        cell: (policy) => (
                          <div className="flex items-center gap-2">
                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                              <FileText className="h-3.5 w-3.5 text-primary" />
                            </div>
                            <span className="font-medium">{policy.name}</span>
                          </div>
                        ),
                      },
                      {
                        key: "description",
                        header: "Description",
                        cell: (policy) => (
                          <span className="text-xs text-muted-foreground">{policy.description}</span>
                        ),
                      },
                      {
                        key: "rulesCount",
                        header: "Rules",
                        className: "text-right",
                        cell: (policy) => (
                          <span className="text-xs tabular-nums">{policy.rulesCount}</span>
                        ),
                      },
                      {
                        key: "enabled",
                        header: "Enabled",
                        className: "text-center",
                        cell: (policy) => (
                          <Switch checked={policy.enabled} disabled className="mx-auto" />
                        ),
                      },
                    ]}
                    data={policyList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="audit" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Audit Log</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<AuditEntry>
                    columns={[
                      {
                        key: "actor",
                        header: "Actor",
                        cell: (entry) => (
                          <span className="text-xs font-medium">{entry.actor}</span>
                        ),
                      },
                      {
                        key: "action",
                        header: "Action",
                        cell: (entry) => (
                          <Badge variant="secondary" className="text-[10px] font-mono">
                            {entry.action}
                          </Badge>
                        ),
                      },
                      {
                        key: "resource",
                        header: "Resource",
                        cell: (entry) => (
                          <span className="text-xs text-muted-foreground">{entry.resource}</span>
                        ),
                      },
                      {
                        key: "details",
                        header: "Details",
                        cell: (entry) => (
                          <span className="text-xs text-muted-foreground max-w-[200px] truncate block">
                            {entry.details}
                          </span>
                        ),
                      },
                      {
                        key: "ip",
                        header: "IP",
                        cell: (entry) => (
                          <span className="text-xs font-mono text-muted-foreground">{entry.ip}</span>
                        ),
                      },
                      {
                        key: "timestamp",
                        header: "Timestamp",
                        className: "text-right",
                        cell: (entry) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{entry.timestamp}</span>
                        ),
                      },
                    ]}
                    data={auditList}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}
