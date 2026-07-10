"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  Settings, Flag, ToggleLeft, Sliders, FileJson,
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

type Environment = "development" | "staging" | "production";

interface FeatureFlag {
  id: string;
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  environment: Environment;
  updatedAt: string;
}

interface RuntimeConfig {
  id: string;
  key: string;
  value: string;
  type: "string" | "number" | "boolean" | "json";
  description: string;
  updatedAt: string;
}

interface Profile {
  id: string;
  name: string;
  description: string;
  configKeyCount: number;
  active: boolean;
}

const featureFlags: FeatureFlag[] = [
  { id: "ff1", key: "agent.auto_scaling", name: "Auto Scaling", description: "Enable automatic agent pod scaling based on load", enabled: true, environment: "production", updatedAt: "2026-06-29" },
  { id: "ff2", key: "workflow.parallel_exec", name: "Parallel Execution", description: "Allow parallel workflow branch execution", enabled: true, environment: "production", updatedAt: "2026-06-28" },
  { id: "ff3", key: "memory.external_indexing", name: "External Indexing", description: "Use external vector store for memory indexing", enabled: false, environment: "staging", updatedAt: "2026-06-27" },
  { id: "ff4", key: "auth.sso_enabled", name: "SSO Authentication", description: "Enable single sign-on for all users", enabled: true, environment: "production", updatedAt: "2026-06-25" },
  { id: "ff5", key: "tools.webhook_retries", name: "Webhook Retries", description: "Automatically retry failed webhook deliveries", enabled: true, environment: "production", updatedAt: "2026-06-24" },
  { id: "ff6", key: "analytics.realtime", name: "Real-time Analytics", description: "Stream analytics data in real-time dashboards", enabled: false, environment: "development", updatedAt: "2026-06-23" },
  { id: "ff7", key: "extensions.sandbox", name: "Extension Sandbox", description: "Run third-party extensions in isolated sandbox", enabled: true, environment: "staging", updatedAt: "2026-06-22" },
  { id: "ff8", key: "ui.beta_workspace", name: "Beta Workspace UI", description: "New workspace layout with enhanced navigation", enabled: false, environment: "development", updatedAt: "2026-06-21" },
];

const runtimeConfigs: RuntimeConfig[] = [
  { id: "rc1", key: "server.max_connections", value: "100", type: "number", description: "Maximum concurrent connections to the API server", updatedAt: "2026-06-30" },
  { id: "rc2", key: "cache.ttl_seconds", value: "3600", type: "number", description: "Default cache TTL in seconds", updatedAt: "2026-06-29" },
  { id: "rc3", key: "logging.level", value: "info", type: "string", description: "Global logging verbosity level", updatedAt: "2026-06-28" },
  { id: "rc4", key: "rate_limit.enabled", value: "true", type: "boolean", description: "Enable rate limiting on public endpoints", updatedAt: "2026-06-27" },
  { id: "rc5", key: "database.pool_options", value: '{"min":2,"max":20,"acquire":30000}', type: "json", description: "Database connection pool configuration", updatedAt: "2026-06-26" },
  { id: "rc6", key: "storage.backend", value: "s3", type: "string", description: "Active storage backend provider", updatedAt: "2026-06-25" },
];

const profiles: Profile[] = [
  { id: "p1", name: "Development", description: "Local development environment with debugging enabled", configKeyCount: 24, active: true },
  { id: "p2", name: "Staging", description: "Pre-production environment for integration testing", configKeyCount: 31, active: true },
  { id: "p3", name: "Production", description: "Live environment serving end-user traffic", configKeyCount: 38, active: true },
  { id: "p4", name: "DR Site", description: "Disaster recovery region with reduced capacity", configKeyCount: 18, active: false },
];

const environmentVariant: Record<Environment, "default" | "warning" | "secondary"> = {
  development: "secondary",
  staging: "warning",
  production: "default",
};

const typeVariant: Record<string, "default" | "secondary" | "info" | "outline"> = {
  string: "default",
  number: "secondary",
  boolean: "info",
  json: "outline",
};

export default function ConfigurationCenterPage() {
  const { data: flagsData } = useData(() => api.config.featureFlags());
  const { data: runtimeData } = useData(() => api.config.runtimeConfig());
  const { data: profilesData } = useData(() => api.config.profiles());
  const flagList = (flagsData || featureFlags) as FeatureFlag[];
  const configList = (runtimeData || runtimeConfigs) as RuntimeConfig[];
  const profileList = (profilesData || profiles) as Profile[];
  const enabledFlags = flagList.filter((f) => f.enabled).length;
  const activeProfiles = profileList.filter((p) => p.active).length;

  return (
    <div className="pb-8">
      <PageHeader
        title="Configuration Center"
        description="Manage platform configuration exposed through approved administrative APIs"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Flags" value={flagList.length} icon={Flag} />
          <StatCard title="Enabled" value={enabledFlags} icon={ToggleLeft} description={`${flagList.length - enabledFlags} disabled`} trend={{ value: Math.round((enabledFlags / flagList.length) * 100), positive: true }} />
          <StatCard title="Runtime Configs" value={configList.length} icon={Sliders} />
          <StatCard title="Active Profiles" value={activeProfiles} icon={FileJson} description={`${profileList.length} total`} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="feature-flags">
            <TabsList>
              <TabsTrigger value="feature-flags">Feature Flags</TabsTrigger>
              <TabsTrigger value="runtime-config">Runtime Configuration</TabsTrigger>
              <TabsTrigger value="profiles">Profiles</TabsTrigger>
            </TabsList>

            <TabsContent value="feature-flags" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Feature Flags</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<FeatureFlag>
                    columns={[
                      {
                        key: "key",
                        header: "Key",
                        cell: (flag) => (
                          <span className="text-xs font-mono font-medium">{flag.key}</span>
                        ),
                      },
                      {
                        key: "name",
                        header: "Name",
                        cell: (flag) => (
                          <span className="text-xs font-medium">{flag.name}</span>
                        ),
                      },
                      {
                        key: "description",
                        header: "Description",
                        cell: (flag) => (
                          <span className="text-xs text-muted-foreground max-w-[240px] truncate block">{flag.description}</span>
                        ),
                      },
                      {
                        key: "enabled",
                        header: "Enabled",
                        className: "text-center",
                        cell: (flag) => (
                          <Switch checked={flag.enabled} disabled className="mx-auto" />
                        ),
                      },
                      {
                        key: "environment",
                        header: "Environment",
                        cell: (flag) => (
                          <Badge variant={environmentVariant[flag.environment]} className="text-[10px]">
                            {flag.environment}
                          </Badge>
                        ),
                      },
                      {
                        key: "updatedAt",
                        header: "Updated",
                        className: "text-right",
                        cell: (flag) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{flag.updatedAt}</span>
                        ),
                      },
                    ]}
                    data={flagList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="runtime-config" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Runtime Configuration</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<RuntimeConfig>
                    columns={[
                      {
                        key: "key",
                        header: "Key",
                        cell: (cfg) => (
                          <span className="text-xs font-mono font-medium">{cfg.key}</span>
                        ),
                      },
                      {
                        key: "value",
                        header: "Value",
                        cell: (cfg) => (
                          <span className="text-xs font-mono text-muted-foreground max-w-[180px] truncate block">{cfg.value}</span>
                        ),
                      },
                      {
                        key: "type",
                        header: "Type",
                        cell: (cfg) => (
                          <Badge variant={typeVariant[cfg.type]} className="text-[10px] font-mono">
                            {cfg.type}
                          </Badge>
                        ),
                      },
                      {
                        key: "description",
                        header: "Description",
                        cell: (cfg) => (
                          <span className="text-xs text-muted-foreground max-w-[200px] truncate block">{cfg.description}</span>
                        ),
                      },
                      {
                        key: "updatedAt",
                        header: "Updated",
                        className: "text-right",
                        cell: (cfg) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{cfg.updatedAt}</span>
                        ),
                      },
                      {
                        key: "actions",
                        header: "",
                        className: "text-right",
                        cell: () => (
                          <Button variant="ghost" size="sm" className="h-7 text-xs">
                            Edit
                          </Button>
                        ),
                      },
                    ]}
                    data={configList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="profiles" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Configuration Profiles</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<Profile>
                    columns={[
                      {
                        key: "name",
                        header: "Name",
                        cell: (profile) => (
                          <div className="flex items-center gap-2">
                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                              <FileJson className="h-3.5 w-3.5 text-primary" />
                            </div>
                            <span className="font-medium">{profile.name}</span>
                          </div>
                        ),
                      },
                      {
                        key: "description",
                        header: "Description",
                        cell: (profile) => (
                          <span className="text-xs text-muted-foreground">{profile.description}</span>
                        ),
                      },
                      {
                        key: "configKeyCount",
                        header: "Config Keys",
                        className: "text-right",
                        cell: (profile) => (
                          <span className="text-xs tabular-nums">{profile.configKeyCount}</span>
                        ),
                      },
                      {
                        key: "active",
                        header: "Status",
                        className: "text-center",
                        cell: (profile) => (
                          profile.active
                            ? <Badge variant="success" className="text-[10px]">Active</Badge>
                            : <Badge variant="secondary" className="text-[10px]">Inactive</Badge>
                        ),
                      },
                    ]}
                    data={profileList}
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
