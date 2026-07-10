"use client";

import { motion } from "framer-motion";
import { Puzzle } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import type { IntegrationContract } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function Integrations() {
  const { integrationContracts } = useDesktopStore();

  const columns: Column<IntegrationContract>[] = [
    { key: "name", header: "Name", sortable: true, render: (i) => <span className="font-medium">{i.name}</span> },
    { key: "application", header: "Application", render: (i) => <span className="text-muted-foreground">{i.application}</span> },
    {
      key: "type", header: "Type", sortable: true, render: (i) => (
        <Badge variant="outline" className="capitalize">{i.type.replace("-", " ")}</Badge>
      ),
    },
    {
      key: "capabilities", header: "Capabilities", render: (i) => (
        <div className="flex flex-wrap gap-1">
          {i.capabilities.map((cap) => <Badge key={cap} variant="secondary" className="text-[10px]">{cap}</Badge>)}
        </div>
      ),
    },
    {
      key: "protocols", header: "Protocols", render: (i) => (
        <div className="flex flex-wrap gap-1">
          {i.protocols.map((p) => <Badge key={p} variant="outline" className="text-[10px]">{p}</Badge>)}
        </div>
      ),
    },
    { key: "version", header: "Version", render: (i) => <span className="text-muted-foreground text-[11px]">v{i.version}</span> },
    {
      key: "available", header: "Available", sortable: true, render: (i) => (
        <Badge variant={i.available ? "success" : "secondary"}>
          {i.available ? "Available" : "Unavailable"}
        </Badge>
      ),
    },
  ];

  const browserInt = integrationContracts.filter((i) => i.type === "browser");
  const officeInt = integrationContracts.filter((i) => i.type === "office");
  const ideInt = integrationContracts.filter((i) => i.type === "ide");
  const otherInt = integrationContracts.filter((i) => !["browser", "office", "ide"].includes(i.type));

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="Integrations"
          description="Connected applications and services"
        />
      </motion.div>

      {integrationContracts.length === 0 ? (
        <motion.div variants={itemVariants}>
          <EmptyState
            icon={Puzzle}
            title="No integrations"
            description="Integration contracts will appear here when applications are connected"
          />
        </motion.div>
      ) : (
        <>
          {browserInt.length > 0 && (
            <motion.div variants={itemVariants}>
              <SectionHeader title="Browser Integrations" description={`${browserInt.length} connected`} />
              <DataTable columns={columns} data={browserInt} keyField="id" />
            </motion.div>
          )}

          {officeInt.length > 0 && (
            <motion.div variants={itemVariants}>
              <SectionHeader title="Office Integrations" description={`${officeInt.length} connected`} />
              <DataTable columns={columns} data={officeInt} keyField="id" />
            </motion.div>
          )}

          {ideInt.length > 0 && (
            <motion.div variants={itemVariants}>
              <SectionHeader title="IDE Integrations" description={`${ideInt.length} connected`} />
              <DataTable columns={columns} data={ideInt} keyField="id" />
            </motion.div>
          )}

          {otherInt.length > 0 && (
            <motion.div variants={itemVariants}>
              <SectionHeader title="Other Integrations" description={`${otherInt.length} connected`} />
              <DataTable columns={columns} data={otherInt} keyField="id" />
            </motion.div>
          )}
        </>
      )}
    </motion.div>
  );
}
