"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable, type Column } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BookType, Send, Code, FileJson } from "lucide-react";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface Endpoint {
  id: string;
  method: HttpMethod;
  path: string;
  description: string;
  version: string;
  parameters: { name: string; type: string; required: boolean; description: string }[];
  exampleRequest: string;
  exampleResponse: string;
}

const methodColor: Record<HttpMethod, string> = {
  GET: "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20",
  POST: "bg-blue-500/10 text-blue-500 hover:bg-blue-500/20",
  PUT: "bg-orange-500/10 text-orange-500 hover:bg-orange-500/20",
  PATCH: "bg-purple-500/10 text-purple-500 hover:bg-purple-500/20",
  DELETE: "bg-red-500/10 text-red-500 hover:bg-red-500/20",
};

const endpoints: Endpoint[] = [
  {
    id: "1", method: "GET", path: "/api/v1/agents", description: "List all registered agents", version: "1.0",
    parameters: [{ name: "page", type: "integer", required: false, description: "Page number for pagination" }, { name: "limit", type: "integer", required: false, description: "Items per page" }, { name: "status", type: "string", required: false, description: "Filter by agent status" }],
    exampleRequest: "GET /api/v1/agents?page=1&limit=10&status=active",
    exampleResponse: `{
  "data": [
    { "id": "agent_01", "name": "CodeAssistant", "status": "active", "model": "gpt-4o" }
  ],
  "pagination": { "page": 1, "limit": 10, "total": 42 }
}`,
  },
  {
    id: "2", method: "POST", path: "/api/v1/agents", description: "Create a new agent", version: "1.0",
    parameters: [{ name: "name", type: "string", required: true, description: "Agent display name" }, { name: "model", type: "string", required: true, description: "Model identifier" }, { name: "instructions", type: "string", required: false, description: "System instructions" }],
    exampleRequest: `POST /api/v1/agents
Content-Type: application/json

{ "name": "MyAgent", "model": "gpt-4o", "instructions": "You are a helpful assistant" }`,
    exampleResponse: `{
  "id": "agent_99",
  "name": "MyAgent",
  "model": "gpt-4o",
  "status": "idle",
  "createdAt": "2026-06-30T18:00:00Z"
}`,
  },
  {
    id: "3", method: "GET", path: "/api/v1/agents/{id}", description: "Get agent details by ID", version: "1.0",
    parameters: [{ name: "id", type: "string", required: true, description: "Agent unique identifier" }],
    exampleRequest: "GET /api/v1/agents/agent_01",
    exampleResponse: `{
  "id": "agent_01",
  "name": "CodeAssistant",
  "status": "active",
  "model": "gpt-4o",
  "capabilities": ["code-gen", "refactor"],
  "metrics": { "taskCount": 1423, "uptime": "99.97%" }
}`,
  },
  {
    id: "4", method: "DELETE", path: "/api/v1/agents/{id}", description: "Remove an agent", version: "1.0",
    parameters: [{ name: "id", type: "string", required: true, description: "Agent unique identifier" }],
    exampleRequest: "DELETE /api/v1/agents/agent_01",
    exampleResponse: `{ "success": true, "message": "Agent agent_01 deleted" }`,
  },
  {
    id: "5", method: "GET", path: "/api/v1/workflows", description: "List all workflows", version: "1.0",
    parameters: [{ name: "page", type: "integer", required: false, description: "Page number" }, { name: "status", type: "string", required: false, description: "Filter by workflow status" }],
    exampleRequest: "GET /api/v1/workflows?page=1&status=published",
    exampleResponse: `{
  "data": [
    { "id": "wf_01", "name": "Data Pipeline", "version": "v2.1", "status": "published" }
  ],
  "total": 12
}`,
  },
  {
    id: "6", method: "POST", path: "/api/v1/workflows", description: "Create a new workflow", version: "1.0",
    parameters: [{ name: "name", type: "string", required: true, description: "Workflow name" }, { name: "nodes", type: "array", required: true, description: "Array of workflow nodes" }],
    exampleRequest: `POST /api/v1/workflows
Content-Type: application/json

{ "name": "MyWorkflow", "nodes": [{ "type": "trigger", "id": "node_1" }] }`,
    exampleResponse: `{ "id": "wf_99", "name": "MyWorkflow", "status": "draft", "nodeCount": 1 }`,
  },
  {
    id: "7", method: "PUT", path: "/api/v1/workflows/{id}", description: "Update an existing workflow", version: "1.0",
    parameters: [{ name: "id", type: "string", required: true, description: "Workflow ID" }, { name: "name", type: "string", required: false, description: "Updated name" }, { name: "nodes", type: "array", required: false, description: "Updated nodes" }],
    exampleRequest: `PUT /api/v1/workflows/wf_01
Content-Type: application/json

{ "name": "Updated Pipeline", "nodes": [{ "type": "trigger", "id": "node_1" }] }`,
    exampleResponse: `{ "id": "wf_01", "name": "Updated Pipeline", "status": "draft", "updatedAt": "2026-06-30T18:05:00Z" }`,
  },
  {
    id: "8", method: "GET", path: "/api/v1/tools", description: "List available tools", version: "1.1",
    parameters: [{ name: "category", type: "string", required: false, description: "Filter by tool category" }],
    exampleRequest: "GET /api/v1/tools?category=Network",
    exampleResponse: `{
  "data": [
    { "id": "tool_01", "name": "WebScraper", "category": "Network", "status": "active" }
  ]
}`,
  },
  {
    id: "9", method: "POST", path: "/api/v1/tools/{id}/execute", description: "Execute a tool", version: "1.1",
    parameters: [{ name: "id", type: "string", required: true, description: "Tool ID" }, { name: "params", type: "object", required: true, description: "Tool execution parameters" }],
    exampleRequest: `POST /api/v1/tools/tool_01/execute
Content-Type: application/json

{ "params": { "url": "https://example.com" } }`,
    exampleResponse: `{ "executionId": "exec_123", "status": "success", "result": { "content": "...", "metadata": {} }, "duration": "234ms" }`,
  },
  {
    id: "10", method: "GET", path: "/api/v1/memory", description: "Query agent memory store", version: "1.0",
    parameters: [{ name: "agentId", type: "string", required: true, description: "Agent ID" }, { name: "query", type: "string", required: false, description: "Semantic search query" }, { name: "limit", type: "integer", required: false, description: "Max results" }],
    exampleRequest: "GET /api/v1/memory?agentId=agent_01&query=recent&limit=5",
    exampleResponse: `{
  "data": [
    { "id": "mem_01", "content": "User requested code review", "timestamp": "2026-06-30T17:00:00Z", "score": 0.95 }
  ]
}`,
  },
  {
    id: "11", method: "POST", path: "/api/v1/chat/completions", description: "Send a chat completion request", version: "1.0",
    parameters: [{ name: "model", type: "string", required: true, description: "Model identifier" }, { name: "messages", type: "array", required: true, description: "Chat messages" }, { name: "temperature", type: "number", required: false, description: "Sampling temperature" }],
    exampleRequest: `POST /api/v1/chat/completions
Content-Type: application/json

{ "model": "gpt-4o", "messages": [{ "role": "user", "content": "Hello" }], "temperature": 0.7 }`,
    exampleResponse: `{
  "id": "chatcmpl_abc123",
  "choices": [{ "index": 0, "message": { "role": "assistant", "content": "Hi there!" } }],
  "usage": { "promptTokens": 10, "completionTokens": 5, "totalTokens": 15 }
}`,
  },
  {
    id: "12", method: "PATCH", path: "/api/v1/agents/{id}/status", description: "Update agent status", version: "1.0",
    parameters: [{ name: "id", type: "string", required: true, description: "Agent ID" }, { name: "status", type: "string", required: true, description: "New status (active/idle/busy/error)" }],
    exampleRequest: `PATCH /api/v1/agents/agent_01/status
Content-Type: application/json

{ "status": "busy" }`,
    exampleResponse: `{ "id": "agent_01", "status": "busy", "updatedAt": "2026-06-30T18:10:00Z" }`,
  },
];

const methods: HttpMethod[] = ["GET", "POST", "PUT", "PATCH", "DELETE"];

export default function ApiExplorerPage() {
  const { data: apiEndpoints, loading, error } = useData(() => api.apiExplorer.endpoints());
  const endpointList = (apiEndpoints || endpoints) as Endpoint[];
  const totalEndpoints = endpointList.length;
  const getCount = endpointList.filter((e) => e.method === "GET").length;
  const postCount = endpointList.filter((e) => e.method === "POST").length;
  const otherCount = endpointList.filter((e) => !["GET", "POST"].includes(e.method)).length;

  const endpointColumns: Column<Endpoint>[] = [
    {
      key: "method",
      header: "Method",
      cell: (ep) => (
        <Badge variant="outline" className={`text-[11px] font-mono font-semibold border-0 ${methodColor[ep.method]}`}>
          {ep.method}
        </Badge>
      ),
    },
    {
      key: "path",
      header: "Path",
      cell: (ep) => <span className="font-mono text-xs font-medium">{ep.path}</span>,
    },
    {
      key: "description",
      header: "Description",
      cell: (ep) => <span className="text-muted-foreground">{ep.description}</span>,
    },
    {
      key: "version",
      header: "Version",
      className: "text-right",
      cell: (ep) => <Badge variant="secondary" className="text-[10px]">v{ep.version}</Badge>,
    },
  ];

  return (
    <div className="pb-8">
      <PageHeader
        title="API Explorer"
        description="Interactive explorer for the Service Gateway"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Endpoints" value={totalEndpoints} icon={BookType} />
          <StatCard title="GET" value={getCount} icon={Code} />
          <StatCard title="POST" value={postCount} icon={Send} />
          <StatCard title="Other Methods" value={otherCount} icon={FileJson} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Request Builder</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-2">
                <div className="w-32">
                  <Select defaultValue="GET">
                    <SelectTrigger className="h-9 text-xs">
                      <SelectValue placeholder="Method" />
                    </SelectTrigger>
                    <SelectContent>
                      {methods.map((m) => (
                        <SelectItem key={m} value={m} className="text-xs">
                          <span className={`font-mono font-semibold ${m === "GET" ? "text-emerald-500" : m === "POST" ? "text-blue-500" : m === "PUT" ? "text-orange-500" : m === "PATCH" ? "text-purple-500" : "text-red-500"}`}>
                            {m}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex-1">
                  <Input
                    placeholder="/api/v1/agents"
                    className="h-9 font-mono text-xs"
                    defaultValue="/api/v1/agents"
                  />
                </div>
                <Button size="sm" className="h-9 gap-1.5">
                  <Send className="h-3.5 w-3.5" />
                  Send
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardContent className="p-0">
              <Tabs defaultValue="endpoints" className="w-full">
                <div className="border-b border-studio-border px-4 pt-3">
                  <TabsList>
                    <TabsTrigger value="endpoints" className="gap-1.5">
                      <Code className="h-3.5 w-3.5" />
                      Endpoints
                    </TabsTrigger>
                    <TabsTrigger value="documentation" className="gap-1.5">
                      <BookType className="h-3.5 w-3.5" />
                      Documentation
                    </TabsTrigger>
                  </TabsList>
                </div>

                <TabsContent value="endpoints" className="m-0">
                  <DataTable
                    columns={endpointColumns}
                    data={endpointList}
                    emptyMessage="No endpoints found"
                  />
                </TabsContent>

                <TabsContent value="documentation" className="m-0 p-4">
                  <div className="space-y-6">
                    {endpointList.slice(0, 1).map((ep) => (
                      <div key={ep.id} className="space-y-4">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className={`text-xs font-mono font-semibold border-0 ${methodColor[ep.method]}`}>
                            {ep.method}
                          </Badge>
                          <code className="text-sm font-mono font-medium">{ep.path}</code>
                          <Badge variant="secondary" className="text-[10px] ml-auto">v{ep.version}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{ep.description}</p>

                        <div>
                          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Parameters</h4>
                          <div className="overflow-x-auto rounded-lg border">
                            <table className="w-full text-xs">
                              <thead>
                                <tr className="border-b bg-muted/50">
                                  <th className="px-3 py-2 text-left font-medium text-muted-foreground">Name</th>
                                  <th className="px-3 py-2 text-left font-medium text-muted-foreground">Type</th>
                                  <th className="px-3 py-2 text-left font-medium text-muted-foreground">Required</th>
                                  <th className="px-3 py-2 text-left font-medium text-muted-foreground">Description</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y">
                                {ep.parameters.map((param) => (
                                  <tr key={param.name} className="hover:bg-muted/30">
                                    <td className="px-3 py-2 font-mono font-medium">{param.name}</td>
                                    <td className="px-3 py-2 text-muted-foreground"><code className="text-[10px]">{param.type}</code></td>
                                    <td className="px-3 py-2">
                                      {param.required ? (
                                        <Badge variant="destructive" className="text-[9px] h-4">Required</Badge>
                                      ) : (
                                        <Badge variant="outline" className="text-[9px] h-4">Optional</Badge>
                                      )}
                                    </td>
                                    <td className="px-3 py-2 text-muted-foreground">{param.description}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                        <div className="grid gap-4 sm:grid-cols-2">
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Example Request</h4>
                            <pre className="rounded-lg bg-muted p-3 text-xs font-mono overflow-x-auto whitespace-pre-wrap">{ep.exampleRequest}</pre>
                          </div>
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Example Response</h4>
                            <pre className="rounded-lg bg-muted p-3 text-xs font-mono overflow-x-auto whitespace-pre-wrap">{ep.exampleResponse}</pre>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
