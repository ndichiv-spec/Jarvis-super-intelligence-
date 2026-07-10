"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/shared/empty-state";
import { BookOpen, Search, Plus, FileText, ExternalLink, Clock, Tag, Layers } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import { motion } from "framer-motion";

const documents = [
  { id: "1", title: "System Architecture Overview", summary: "High-level architecture documentation for the JARVIS platform", collection: "Technical Docs", type: "document" as const, tags: ["architecture", "system-design"], updatedAt: new Date(Date.now() - 86400000) },
  { id: "2", title: "API Reference v2.0", summary: "Complete API endpoint reference with examples", collection: "Technical Docs", type: "reference" as const, tags: ["api", "integration"], updatedAt: new Date(Date.now() - 172800000) },
  { id: "3", title: "Q1 2026 Research Findings", summary: "Compiled research data and insights from Q1", collection: "Research", type: "document" as const, tags: ["research", "quarterly"], updatedAt: new Date(Date.now() - 259200000) },
  { id: "4", title: "Market Analysis Report", summary: "Competitive analysis and market positioning", collection: "Business", type: "source" as const, tags: ["market", "strategy"], updatedAt: new Date(Date.now() - 345600000) },
  { id: "5", title: "Meeting Notes: Architecture Review", summary: "Notes from the architecture review meeting on June 15", collection: "Meetings", type: "note" as const, tags: ["meeting", "architecture"], updatedAt: new Date(Date.now() - 432000000) },
  { id: "6", title: "Security Best Practices Guide", summary: "Security guidelines and best practices for development", collection: "Technical Docs", type: "reference" as const, tags: ["security", "best-practices"], updatedAt: new Date(Date.now() - 604800000) },
];

const typeIcons: Record<string, React.ElementType> = {
  document: FileText,
  reference: BookOpen,
  source: ExternalLink,
  note: FileText,
};

const collections = ["All", "Technical Docs", "Research", "Business", "Meetings"];
const docTypes = ["All", "document", "reference", "source", "note"];

export default function KnowledgePage() {
  const [search, setSearch] = useState("");
  const [collectionFilter, setCollectionFilter] = useState("All");

  const filtered = documents.filter((d) => {
    if (collectionFilter !== "All" && d.collection !== collectionFilter) return false;
    if (search && !d.title.toLowerCase().includes(search.toLowerCase()) && !d.summary.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="pb-8">
      <PageHeader
        title="Knowledge Center"
        description="Browse and search your knowledge collections"
        actions={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Document
          </Button>
        }
      />

      <div className="px-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search knowledge..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <div className="flex gap-2 flex-wrap">
          {collections.map((c) => (
            <Badge
              key={c}
              variant={collectionFilter === c ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setCollectionFilter(c)}
            >
              {c}
            </Badge>
          ))}
        </div>

        {filtered.length === 0 ? (
          <EmptyState
            icon={BookOpen}
            title="No documents found"
            description={search ? "Try a different search term" : "Your knowledge base is empty"}
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {filtered.map((doc, i) => {
              const Icon = typeIcons[doc.type] || FileText;
              return (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                >
                  <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 shrink-0">
                          <Icon className="h-4 w-4 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <CardTitle className="text-sm">{doc.title}</CardTitle>
                            <Badge variant="outline" className="text-[10px]">{doc.type}</Badge>
                          </div>
                          <CardDescription className="text-xs">{doc.summary}</CardDescription>
                          <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Layers className="h-3 w-3" />
                              {doc.collection}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatRelativeTime(doc.updatedAt)}
                            </span>
                          </div>
                          {doc.tags.length > 0 && (
                            <div className="flex gap-1 mt-2">
                              {doc.tags.map((tag) => (
                                <Badge key={tag} variant="secondary" className="text-[10px]">
                                  <Tag className="h-2.5 w-2.5 mr-1" />
                                  {tag}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
