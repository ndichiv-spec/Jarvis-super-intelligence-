"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, MessageSquare, History, Search, Trash2 } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";

interface Conversation {
  id: string;
  title: string;
  preview: string;
  date: Date;
}

interface ConversationListProps {
  conversations: Conversation[];
  activeId?: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete?: (id: string) => void;
}

export function ConversationList({ conversations, activeId, onSelect, onNew, onDelete }: ConversationListProps) {
  const [search, setSearch] = useState("");

  const filtered = search
    ? conversations.filter(
        (c) =>
          c.title.toLowerCase().includes(search.toLowerCase()) ||
          c.preview.toLowerCase().includes(search.toLowerCase()),
      )
    : conversations;

  return (
    <div className="hidden md:flex w-64 flex-col border-r bg-muted/30">
      <div className="p-3 space-y-2">
        <Button className="w-full justify-start" size="sm" onClick={onNew}>
          <Plus className="mr-2 h-4 w-4" />
          New Conversation
        </Button>
        <div className="relative">
          <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search conversations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 h-8 text-xs"
          />
        </div>
      </div>
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-1">
          {filtered.length === 0 ? (
            <p className="px-3 py-4 text-xs text-center text-muted-foreground">
              {search ? "No matching conversations" : "No conversations yet"}
            </p>
          ) : (
            filtered.map((conv) => (
              <button
                key={conv.id}
                onClick={() => onSelect(conv.id)}
                className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-accent group ${
                  conv.id === activeId ? "bg-accent" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                    <span className="font-medium truncate">{conv.title}</span>
                  </div>
                  {onDelete && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(conv.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 rounded"
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </button>
                  )}
                </div>
                <p className="mt-0.5 text-xs text-muted-foreground truncate pl-6">{conv.preview}</p>
                <p className="text-[10px] text-muted-foreground pl-6">{formatRelativeTime(conv.date)}</p>
              </button>
            ))
          )}
        </div>
      </ScrollArea>
      <div className="p-3 border-t">
        <Button variant="ghost" size="sm" className="w-full justify-start">
          <History className="mr-2 h-4 w-4" />
          View History
        </Button>
      </div>
    </div>
  );
}
