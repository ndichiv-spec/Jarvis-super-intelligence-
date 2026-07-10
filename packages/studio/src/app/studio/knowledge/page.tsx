"use client";

import { useState } from "react";
import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { StatCard } from "@/components/shared/stat-card";
import { EmptyState } from "@/components/shared/empty-state";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { BookOpen, Search, GitBranch, Tag, ArrowRight, FileText, Database } from "lucide-react";
import { motion } from "framer-motion";
import { formatRelativeTime } from "@/lib/utils";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const MOCK_COLLECTIONS = [
  { id: "c1", name: "Research Papers", description: "Academic papers and publications", type: "vector" as const, documentCount: 342, updatedAt: new Date("2026-06-28") },
  { id: "c2", name: "Knowledge Graph", description: "Entity relationship knowledge base", type: "graph" as const, documentCount: 1289, updatedAt: new Date("2026-06-29") },
  { id: "c3", name: "Technical Documentation", description: "API docs, guides, and references", type: "hybrid" as const, documentCount: 567, updatedAt: new Date("2026-06-30") },
  { id: "c4", name: "Conversation History", description: "Agent chat logs and transcripts", type: "vector" as const, documentCount: 8901, updatedAt: new Date("2026-06-29") },
];

const MOCK_DOCUMENTS = [
  { id: "d1", title: "Transformer Architecture Overview", collection: "Research Papers", type: "document" as const, tags: ["deep-learning", "nlp", "transformers"], relationships: ["d2", "d3"], updatedAt: new Date("2026-06-28") },
  { id: "d2", title: "Attention Mechanisms Survey", collection: "Research Papers", type: "reference" as const, tags: ["attention", "survey"], relationships: ["d1", "d4"], updatedAt: new Date("2026-06-27") },
  { id: "d3", title: "Fine-tuning LLMs Guide", collection: "Technical Documentation", type: "document" as const, tags: ["llm", "fine-tuning", "guide"], relationships: ["d1"], updatedAt: new Date("2026-06-30") },
  { id: "d4", title: "Entity Resolution Pipeline", collection: "Knowledge Graph", type: "source" as const, tags: ["pipeline", "entity", "graph"], relationships: ["d2", "d5"], updatedAt: new Date("2026-06-26") },
  { id: "d5", title: "Graph Database Schema Design", collection: "Knowledge Graph", type: "document" as const, tags: ["graph-db", "schema", "design"], relationships: ["d4", "d6"], updatedAt: new Date("2026-06-25") },
  { id: "d6", title: "Vector Search Best Practices", collection: "Technical Documentation", type: "reference" as const, tags: ["vector-search", "indexing"], relationships: ["d5", "d7"], updatedAt: new Date("2026-06-29") },
  { id: "d7", title: "Hybrid Search Implementation", collection: "Technical Documentation", type: "document" as const, tags: ["hybrid", "search", "implementation"], relationships: ["d6", "d8"], updatedAt: new Date("2026-06-28") },
  { id: "d8", title: "Customer Support Transcript", collection: "Conversation History", type: "note" as const, tags: ["support", "customer"], relationships: ["d9"], updatedAt: new Date("2026-06-30") },
  { id: "d9", title: "Agent Reasoning Trace", collection: "Conversation History", type: "source" as const, tags: ["reasoning", "trace", "agent"], relationships: ["d8", "d10"], updatedAt: new Date("2026-06-29") },
  { id: "d10", title: "Knowledge Distillation Methods", collection: "Research Papers", type: "reference" as const, tags: ["distillation", "model-compression"], relationships: ["d1", "d3"], updatedAt: new Date("2026-06-27") },
];

const typeColors: Record<string, "info" | "success" | "warning" | "default"> = {
  vector: "info",
  graph: "success",
  hybrid: "warning",
};

const docTypeColors: Record<string, "default" | "secondary" | "info" | "outline"> = {
  document: "default",
  reference: "secondary",
  source: "info",
  note: "outline",
};

const collectionColumns: Column<typeof MOCK_COLLECTIONS[0]>[] = [
  { key: "name", header: "Name", cell: (c) => <span className="font-medium">{c.name}</span> },
  { key: "description", header: "Description", cell: (c) => <span className="text-muted-foreground">{c.description}</span> },
  {
    key: "type", header: "Type", cell: (c) => (
      <Badge variant={typeColors[c.type]} className="capitalize">{c.type}</Badge>
    ),
  },
  { key: "documentCount", header: "Documents", cell: (c) => c.documentCount.toLocaleString() },
  { key: "updatedAt", header: "Updated", cell: (c) => formatRelativeTime(c.updatedAt) },
];

const documentColumns: Column<typeof MOCK_DOCUMENTS[0]>[] = [
  { key: "title", header: "Title", cell: (d) => <span className="font-medium">{d.title}</span> },
  { key: "collection", header: "Collection", cell: (d) => <span className="text-muted-foreground">{d.collection}</span> },
  {
    key: "type", header: "Type", cell: (d) => (
      <Badge variant={docTypeColors[d.type]} className="capitalize">{d.type}</Badge>
    ),
  },
  {
    key: "tags", header: "Tags", cell: (d) => (
      <div className="flex flex-wrap gap-1">
        {d.tags.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="outline" className="text-[10px]">{tag}</Badge>
        ))}
        {d.tags.length > 3 && (
          <Badge variant="outline" className="text-[10px]">+{d.tags.length - 3}</Badge>
        )}
      </div>
    ),
  },
  {
    key: "relationships", header: "Relationships", cell: (d) => (
      <div className="flex items-center gap-1">
        <GitBranch className="h-3 w-3 text-muted-foreground" />
        <span className="text-xs text-muted-foreground">{d.relationships.length}</span>
      </div>
    ),
  },
  { key: "updatedAt", header: "Updated", cell: (d) => formatRelativeTime(d.updatedAt) },
];

export default function KnowledgePage() {
  const { data: collectionsData, loading, error } = useData(() => api.knowledge.collections());
  const collectionList = (collectionsData || MOCK_COLLECTIONS) as typeof MOCK_COLLECTIONS;
  const documents = MOCK_DOCUMENTS;

  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("collections");

  const totalDocuments = documents.length;
  const totalRelationships = documents.reduce((acc, d) => acc + d.relationships.length, 0);
  const lastUpdated = documents.reduce((latest, d) => d.updatedAt > latest ? d.updatedAt : latest, documents[0].updatedAt);

  const filteredDocuments = documents.filter(
    (d) =>
      d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())) ||
      d.collection.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="pb-8">
      <PageHeader
        title="Knowledge Explorer"
        description="Visualize collections, documents, relationships, and classifications"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Collections" value={collectionList.length} icon={Database} />
          <StatCard title="Total Documents" value={totalDocuments} icon={FileText} />
          <StatCard title="Graph Relationships" value={totalRelationships} icon={GitBranch} />
          <StatCard title="Last Updated" value={formatRelativeTime(lastUpdated)} icon={BookOpen} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardContent className="p-0">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <div className="border-b px-4 py-2">
                  <TabsList>
                    <TabsTrigger value="collections" className="gap-1.5">
                      <Database className="h-4 w-4" />
                      Collections
                    </TabsTrigger>
                    <TabsTrigger value="documents" className="gap-1.5">
                      <FileText className="h-4 w-4" />
                      Documents
                    </TabsTrigger>
                    <TabsTrigger value="search" className="gap-1.5">
                      <Search className="h-4 w-4" />
                      Search
                    </TabsTrigger>
                  </TabsList>
                </div>

                <TabsContent value="collections" className="m-0">
                  <DataTable columns={collectionColumns} data={collectionList} />
                </TabsContent>

                <TabsContent value="documents" className="m-0">
                  <DataTable columns={documentColumns} data={documents} />
                </TabsContent>

                <TabsContent value="search" className="p-4 space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search documents by title, tag, or collection..."
                      className="pl-9"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  {searchQuery.trim() === "" ? (
                    <EmptyState
                      icon={Search}
                      title="Search Knowledge Base"
                      description="Enter a search term to find documents across all collections"
                    />
                  ) : filteredDocuments.length === 0 ? (
                    <EmptyState
                      icon={Search}
                      title="No results found"
                      description={`No documents match "${searchQuery}". Try a different search term.`}
                    />
                  ) : (
                    <div className="rounded-lg border divide-y">
                      {filteredDocuments.map((doc) => (
                        <div key={doc.id} className="flex items-center justify-between px-4 py-3 hover:bg-studio-hover transition-colors">
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium">{doc.title}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-xs text-muted-foreground">{doc.collection}</span>
                              <Badge variant={docTypeColors[doc.type]} className="text-[10px] capitalize">{doc.type}</Badge>
                            </div>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {doc.tags.map((tag) => (
                                <Badge key={tag} variant="outline" className="text-[10px]">{tag}</Badge>
                              ))}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 shrink-0 ml-4">
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <GitBranch className="h-3 w-3" />
                              {doc.relationships.length}
                            </div>
                            <ArrowRight className="h-4 w-4 text-muted-foreground" />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
