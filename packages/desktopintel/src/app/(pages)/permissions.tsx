"use client";

import { motion } from "framer-motion";
import { Shield, Check, X, RotateCcw } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { getPermissionLabel, getPermissionDescription, formatRelativeTime } from "@/lib/utils";
import type { PermissionGrant, PermissionRequest, PermissionEvent } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function PermissionCenter() {
  const { state, grantPermission, denyPermission, revokePermission } = useDesktopStore();
  const { granted, pending, history } = state.permissions;

  const grantedColumns: Column<PermissionGrant>[] = [
    { key: "permission", header: "Permission", render: (p) => <span className="font-medium">{getPermissionLabel(p.permission)}</span> },
    { key: "resource", header: "Resource", render: (p) => <span className="text-muted-foreground">{p.resource}</span> },
    { key: "grantedAt", header: "Granted At", sortable: true, render: (p) => <span className="text-muted-foreground">{formatRelativeTime(p.grantedAt)}</span> },
    { key: "revoked", header: "Revoked", render: (p) => p.revoked ? <Badge variant="destructive">Revoked</Badge> : <Badge variant="success">Active</Badge> },
    {
      key: "actions", header: "Action", render: (p) =>
        !p.revoked ? (
          <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => revokePermission(p.id)}>
            <RotateCcw className="h-3 w-3 mr-1" /> Revoke
          </Button>
        ) : null,
    },
  ];

  const pendingColumns: Column<PermissionRequest>[] = [
    { key: "permission", header: "Permission", render: (r) => <span className="font-medium">{getPermissionLabel(r.permission)}</span> },
    { key: "resource", header: "Resource", render: (r) => <span className="text-muted-foreground">{r.resource}</span> },
    { key: "reason", header: "Reason", render: (r) => <span className="text-muted-foreground text-[11px]">{r.reason}</span> },
    { key: "source", header: "Source", render: (r) => <span className="text-muted-foreground">{r.source}</span> },
    { key: "requestedAt", header: "Requested", sortable: true, render: (r) => <span className="text-muted-foreground">{formatRelativeTime(r.requestedAt)}</span> },
    {
      key: "actions", header: "Actions", render: (r) => (
        <div className="flex gap-1">
          <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-status-success" onClick={() => grantPermission(r.id)}>
            <Check className="h-3.5 w-3.5" />
          </Button>
          <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-status-error" onClick={() => denyPermission(r.id)}>
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      ),
    },
  ];

  const historyColumns: Column<PermissionEvent>[] = [
    { key: "permission", header: "Permission", render: (e) => <span className="font-medium">{getPermissionLabel(e.permission)}</span> },
    {
      key: "action", header: "Action", render: (e) => {
        const variant = e.action === "granted" ? "success" : e.action === "revoked" ? "destructive" : e.action === "denied" ? "warning" : "secondary";
        return <Badge variant={variant}>{e.action}</Badge>;
      },
    },
    { key: "resource", header: "Resource", render: (e) => <span className="text-muted-foreground">{e.resource}</span> },
    { key: "timestamp", header: "Timestamp", sortable: true, render: (e) => <span className="text-muted-foreground">{formatRelativeTime(e.timestamp)}</span> },
    { key: "actor", header: "Actor", render: (e) => <span className="text-muted-foreground">{e.actor}</span> },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="Permission Center"
          description="Manage JARVIS permissions and security policies"
        />
      </motion.div>

      <motion.div variants={itemVariants}>
        <Tabs defaultValue="granted">
          <TabsList>
            <TabsTrigger value="granted">Granted ({granted.length})</TabsTrigger>
            <TabsTrigger value="pending">Pending ({pending.length})</TabsTrigger>
            <TabsTrigger value="history">History ({history.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="granted">
            {granted.length === 0 ? (
              <EmptyState icon={Shield} title="No permissions granted" description="Granted permissions will appear here" />
            ) : (
              <DataTable columns={grantedColumns} data={granted} keyField="id" />
            )}
          </TabsContent>

          <TabsContent value="pending">
            {pending.length === 0 ? (
              <EmptyState icon={Shield} title="No pending requests" description="Permission requests from agents will appear here" />
            ) : (
              <DataTable columns={pendingColumns} data={pending} keyField="id" />
            )}
          </TabsContent>

          <TabsContent value="history">
            {history.length === 0 ? (
              <EmptyState icon={Shield} title="No permission history" description="Permission events will be logged here" />
            ) : (
              <DataTable columns={historyColumns} data={history} keyField="id" />
            )}
          </TabsContent>
        </Tabs>
      </motion.div>
    </motion.div>
  );
}
