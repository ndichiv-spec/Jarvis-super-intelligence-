"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { ConversationList } from "@/components/workspace/conversation-list";
import {
  Send,
  Plus,
  Sparkles,
  Code,
  Image,
  Paperclip,
  Bot,
  StopCircle,
  MessageSquare,
  User,
  Terminal,
  FileText,
  Globe,
  Brain,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  preview: string;
  date: Date;
}

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content: "Hello! I'm your JARVIS AI assistant. I can help you with coding, analysis, research, automation, and much more. What would you like to work on today?",
  timestamp: new Date(),
};

const mockConversations: Conversation[] = [
  { id: "1", title: "Q2 Data Analysis", preview: "Analyzing quarterly metrics and trends", date: new Date(Date.now() - 7200000) },
  { id: "2", title: "Auth System Refactor", preview: "Planning migration to OAuth 2.0", date: new Date(Date.now() - 86400000) },
  { id: "3", title: "API Documentation", preview: "Generating OpenAPI specs", date: new Date(Date.now() - 172800000) },
  { id: "4", title: "Market Research", preview: "Competitive analysis findings", date: new Date(Date.now() - 259200000) },
  { id: "5", title: "Performance Tuning", preview: "Database query optimization", date: new Date(Date.now() - 345600000) },
];

const SUGGESTIONS = [
  { icon: Terminal, text: "Write a Python script to..." },
  { icon: FileText, text: "Summarize this document..." },
  { icon: Globe, text: "Research the latest trends in..." },
  { icon: Brain, text: "Help me understand..." },
];

export default function WorkspacePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeConv, setActiveConv] = useState("1");
  const [conversations, setConversations] = useState<Conversation[]>(mockConversations);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);

    setTimeout(() => {
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I understand your request. Let me process that and provide a helpful response. The platform is currently processing through the Service Gateway.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setIsStreaming(false);
    }, 1500);
  }, [input, isStreaming]);

  const handleNewConversation = useCallback(() => {
    const id = Date.now().toString();
    const conv: Conversation = {
      id,
      title: "New Conversation",
      preview: "Started just now",
      date: new Date(),
    };
    setConversations((prev) => [conv, ...prev]);
    setActiveConv(id);
    setMessages([WELCOME_MESSAGE]);
    inputRef.current?.focus();
  }, []);

  const handleSelectConversation = useCallback((id: string) => {
    setActiveConv(id);
    setMessages([WELCOME_MESSAGE]);
  }, []);

  const handleDeleteConversation = useCallback((id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConv === id) {
      handleNewConversation();
    }
  }, [activeConv, handleNewConversation]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <ConversationList
        conversations={conversations}
        activeId={activeConv}
        onSelect={handleSelectConversation}
        onNew={handleNewConversation}
        onDelete={handleDeleteConversation}
      />

      <div className="flex flex-1 flex-col min-w-0">
        <PageHeader
          title="AI Workspace"
          description="Conversation with JARVIS AI"
        />

        <ScrollArea ref={scrollRef as any} className="flex-1 px-6">
          <div className="max-w-3xl mx-auto space-y-4 py-4">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                >
                  {msg.role === "assistant" && (
                    <Avatar className="h-8 w-8 mt-1 shrink-0">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        <Bot className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  <div className={`max-w-[80%] ${msg.role === "user" ? "order-first" : ""}`}>
                    <div
                      className={`rounded-lg px-4 py-3 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : msg.role === "system"
                          ? "bg-muted/50 border text-muted-foreground italic"
                          : "bg-muted"
                      }`}
                    >
                      {msg.content}
                    </div>
                    <p className="mt-1 text-[10px] text-muted-foreground px-1">
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                  {msg.role === "user" && (
                    <Avatar className="h-8 w-8 mt-1 shrink-0">
                      <AvatarFallback className="bg-secondary text-secondary-foreground">
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </motion.div>
              ))}
              {isStreaming && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3"
                >
                  <Avatar className="h-8 w-8 mt-1 shrink-0">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-muted">
                    <div className="flex gap-1">
                      <span className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="h-2 w-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    <span className="text-sm text-muted-foreground ml-2">Thinking...</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {messages.length === 1 && !isStreaming && (
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="grid grid-cols-2 gap-2 pt-4"
              >
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion.text}
                    onClick={() => {
                      setInput(suggestion.text + " ");
                      inputRef.current?.focus();
                    }}
                    className="flex items-center gap-2 rounded-lg border p-3 text-left text-sm hover:bg-accent transition-colors"
                  >
                    <suggestion.icon className="h-4 w-4 text-primary shrink-0" />
                    <span className="text-muted-foreground">{suggestion.text}</span>
                  </button>
                ))}
              </motion.div>
            )}
          </div>
        </ScrollArea>

        <div className="border-t bg-background px-6 py-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-end gap-2">
              <div className="flex-1 relative">
                <Input
                  ref={inputRef as any}
                  placeholder="Ask JARVIS anything..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                  className="pr-20 h-11"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground">
                    <Paperclip className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <Button onClick={handleSend} disabled={!input.trim() || isStreaming} className="h-11 px-4">
                {isStreaming ? <StopCircle className="h-4 w-4" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
            <div className="mt-2 flex items-center gap-2">
              <Badge variant="secondary" className="text-[10px] gap-1">
                <Code className="h-3 w-3" /> Code
              </Badge>
              <Badge variant="secondary" className="text-[10px] gap-1">
                <Image className="h-3 w-3" /> Image
              </Badge>
              <Badge variant="secondary" className="text-[10px] gap-1">
                <FileText className="h-3 w-3" /> Markdown
              </Badge>
              <span className="text-[10px] text-muted-foreground">Supports code blocks, images, and file attachments</span>
              <kbd className="ml-auto hidden sm:inline-flex h-5 items-center gap-1 rounded border bg-muted px-1.5 text-[10px] font-medium text-muted-foreground">
                ⌘K
              </kbd>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
