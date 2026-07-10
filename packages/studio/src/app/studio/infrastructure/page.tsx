"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { DataTable } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tabs, TabsContent, TabsList, TabsTrigger,
} from "@/components/ui/tabs";
import {
  Server, Database, Zap, Layers, Radio, HardDrive, Activity,
  CheckCircle2, AlertTriangle, MinusCircle, Wrench,
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

type ComponentStatus = "healthy" | "degraded" | "critical" | "maintenance";
type ComponentType = "database" | "cache" | "vector-store" | "message-broker" | "storage" | "adapter";

interface InfrastructureComponent {
  id: string;
  name: string;
  type: ComponentType;
  status: ComponentStatus;
  latency: string;
  uptime: number;
  lastChecked: string;
}

const MOCK_COMPONENTS: InfrastructureComponent[] = [
  { id: "1", name: "PostgreSQL", type: "database", status: "healthy", latency: "4ms", uptime: 99.97, lastChecked: "12s ago" },
  { id: "2", name: "Redis", type: "cache", status: "healthy", latency: "1ms", uptime: 99.99, lastChecked: "8s ago" },
  { id: "3", name: "Qdrant", type: "vector-store", status: "degraded", latency: "87ms", uptime: 98.45, lastChecked: "45s ago" },
  { id: "4", name: "RabbitMQ", type: "message-broker", status: "degraded", latency: "42ms", uptime: 99.12, lastChecked: "30s ago" },
  { id: "5", name: "S3 Storage", type: "storage", status: "healthy", latency: "23ms", uptime: 99.88, lastChecked: "15s ago" },
  { id: "6", name: "Elasticsearch", type: "adapter", status: "critical", latency: "312ms", uptime: 96.21, lastChecked: "10s ago" },
  { id: "7", name: "MongoDB", type: "database", status: "maintenance", latency: "—", uptime: 99.54, lastChecked: "2m ago" },
  { id: "8", name: "Kafka", type: "message-broker", status: "healthy", latency: "8ms", uptime: 99.95, lastChecked: "5s ago" },
];

const typeIconMap: Record<ComponentType, typeof Server> = {
  database: Database,
  cache: Zap,
  "vector-store": Layers,
  "message-broker": Radio,
  storage: HardDrive,
  adapter: Activity,
};

const typeLabelMap: Record<ComponentType, string> = {
  database: "Database",
  cache: "Cache",
  "vector-store": "Vector Store",
  "message-broker": "Message Broker",
  storage: "Storage",
  adapter: "Adapter",
};

const badgeVariantMap: Record<ComponentStatus, "success" | "warning" | "destructive" | "info"> = {
  healthy: "success",
  degraded: "warning",
  critical: "destructive",
  maintenance: "info",
};

export default function InfrastructureMonitorPage() {
  const { data: componentsData, loading, error } = useData(() => api.infrastructure.components());
  const compList = (componentsData || MOCK_COMPONENTS) as InfrastructureComponent[];

  const healthSummaryMetrics = [
    { label: "Total Components", value: compList.length, icon: Server, color: "text-primary" },
    { label: "Healthy", value: compList.filter((c) => c.status === "healthy").length, icon: CheckCircle2, color: "text-status-success" },
    { label: "Degraded", value: compList.filter((c) => c.status === "degraded").length, icon: AlertTriangle, color: "text-status-warning" },
    { label: "Critical", value: compList.filter((c) => c.status === "critical").length, icon: MinusCircle, color: "text-status-error" },
  ];

  const statusCounts = [
    { status: "healthy" as const, label: "Healthy", count: compList.filter((c) => c.status === "healthy").length, icon: CheckCircle2 },
    { status: "degraded" as const, label: "Degraded", count: compList.filter((c) => c.status === "degraded").length, icon: AlertTriangle },
    { status: "critical" as const, label: "Critical", count: compList.filter((c) => c.status === "critical").length, icon: MinusCircle },
    { status: "maintenance" as const, label: "Maintenance", count: compList.filter((c) => c.status === "maintenance").length, icon: Wrench },
  ];

  const componentTypes = [...new Set(compList.map((c) => c.type))];
  return (
    <div className="pb-8">
      <PageHeader
        title="Infrastructure Monitor"
        description="Display infrastructure health"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {compList.map((component) => {
            const Icon = typeIconMap[component.type] || Server;
            return (
              <Card key={component.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                      <Icon className="h-4.5 w-4.5 text-primary" />
                    </div>
                    <StatusDot status={component.status} />
                  </div>
                  <h4 className="text-sm font-medium mb-0.5">{component.name}</h4>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Badge variant="secondary" className="text-[10px]">{typeLabelMap[component.type]}</Badge>
                    <Badge variant={badgeVariantMap[component.status]} className="text-[10px] capitalize">
                      {component.status}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-[11px] text-muted-foreground pt-2 border-t border-studio-border">
                    <div>
                      <span className="block">Latency</span>
                      <span className="font-medium text-foreground">{component.latency}</span>
                    </div>
                    <div>
                      <span className="block">Uptime</span>
                      <span className="font-medium text-foreground">{component.uptime}%</span>
                    </div>
                    <div>
                      <span className="block">Checked</span>
                      <span className="font-medium text-foreground">{component.lastChecked}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="components">
            <TabsList>
              <TabsTrigger value="components">Components</TabsTrigger>
              <TabsTrigger value="health-summary">Health Summary</TabsTrigger>
            </TabsList>

            <TabsContent value="components" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">All Components</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable<InfrastructureComponent>
                    columns={[
                      {
                        key: "name",
                        header: "Name",
                        cell: (component) => {
                          const Icon = typeIconMap[component.type] || Server;
                          return (
                            <div className="flex items-center gap-2">
                              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
                                <Icon className="h-3.5 w-3.5 text-primary" />
                              </div>
                              <span className="font-medium">{component.name}</span>
                            </div>
                          );
                        },
                      },
                      {
                        key: "type",
                        header: "Type",
                        cell: (component) => (
                          <Badge variant="secondary" className="text-[10px]">
                            {typeLabelMap[component.type]}
                          </Badge>
                        ),
                      },
                      {
                        key: "status",
                        header: "Status",
                        cell: (component) => (
                          <div className="flex items-center gap-1.5">
                            <StatusDot status={component.status} />
                            <Badge variant={badgeVariantMap[component.status]} className="text-[10px] capitalize">
                              {component.status}
                            </Badge>
                          </div>
                        ),
                      },
                      {
                        key: "latency",
                        header: "Latency",
                        cell: (component) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{component.latency}</span>
                        ),
                      },
                      {
                        key: "uptime",
                        header: "Uptime %",
                        className: "text-right",
                        cell: (component) => (
                          <span className="text-xs tabular-nums text-muted-foreground">{component.uptime}%</span>
                        ),
                      },
                      {
                        key: "lastChecked",
                        header: "Last Checked",
                        className: "text-right",
                        cell: (component) => (
                          <span className="text-xs text-muted-foreground">{component.lastChecked}</span>
                        ),
                      },
                    ]}
                    data={compList}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="health-summary" className="mt-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-4">
                {healthSummaryMetrics.map((metric) => (
                  <StatCard
                    key={metric.label}
                    title={metric.label}
                    value={metric.value}
                    icon={metric.icon}
                  />
                ))}
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium">Status Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {statusCounts.map((item) => (
                        <div key={item.status} className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                            <item.icon className="h-4 w-4 text-primary" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <StatusDot status={item.status} />
                                <span className="text-sm font-medium">{item.label}</span>
                              </div>
                              <span className="text-sm tabular-nums">{item.count}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium">Component Type Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {componentTypes.map((type) => {
                        const Icon = typeIconMap[type] || Server;
                        const typeComponents = compList.filter((c) => c.type === type);
                        const healthyCount = typeComponents.filter((c) => c.status === "healthy").length;
                        return (
                          <div key={type} className="flex items-center gap-3 rounded-lg border p-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                              <Icon className="h-4 w-4 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">{typeLabelMap[type]}</span>
                                <span className="text-xs text-muted-foreground">({typeComponents.length})</span>
                              </div>
                              <p className="text-[11px] text-muted-foreground mt-0.5">
                                {typeComponents.map((c) => c.name).join(", ")}
                              </p>
                            </div>
                            <div className="flex items-center gap-1">
                              {typeComponents.map((c) => (
                                <StatusDot key={c.id} status={c.status} />
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}
