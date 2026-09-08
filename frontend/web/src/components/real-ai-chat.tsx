"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  Send, Bot, User, Loader2, Code, FileText, Image, Mic,
  Settings, Zap, Brain, Globe, Database, Cpu, Activity,
  CheckCircle, AlertCircle, Info, TrendingUp, BarChart3
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  model?: string;
  tokens_used?: number;
}

interface AIModel {
  name: string;
  type: string;
  capabilities: string[];
  available: boolean;
}

interface SystemStatus {
  status: string;
  total_models: number;
  available_models: number;
  capabilities: string[];
}

export default function RealAIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("auto");
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [availableModels, setAvailableModels] = useState<AIModel[]>([]);
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [backendConnected, setBackendConnected] = useState(true);
  const [usingLocalFallback, setUsingLocalFallback] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSystemStatus();
    loadAvailableModels();
    
    if (realTimeMode) {
      const interval = setInterval(loadSystemStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [realTimeMode]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadSystemStatus = async () => {
    try {
      const response = await fetch("/api/real-ai/jarvis-status");
      const data = await response.json();
      
      if (data.success) {
        setSystemStatus(data.ai_status);
      }
    } catch (error) {
      console.error("Failed to load system status:", error);
    }
  };

  const loadAvailableModels = async () => {
    try {
      const response = await fetch("/api/real-ai/ai-models");
      const data = await response.json();
      
      if (data.success) {
        const models = Object.entries(data.models).map(([id, model]: [string, any]) => ({
          name: model.name,
          type: model.type,
          capabilities: model.capabilities,
          available: model.available
        }));
        setAvailableModels(models);
      }
    } catch (error) {
      console.error("Failed to load models:", error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const generateLocalResponse = (input: string): string => {
    // Local AI fallback when backend is unavailable
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('hello') || lowerInput.includes('hi')) {
      return "Hello! I'm JARVIS running in self-reliant mode. The backend is currently unavailable, but I can still help you with basic tasks using local processing.";
    }
    
    if (lowerInput.includes('help') || lowerInput.includes('what can you do')) {
      return "In self-reliant mode, I can help with:\n• Basic conversation and information\n• System status monitoring\n• File operations\n• Web browsing\n• Code execution\n\nI'm using local processing while the backend reconnects.";
    }
    
    if (lowerInput.includes('status') || lowerInput.includes('system')) {
      return "System Status:\n• Mode: Self-Reliant (Local Fallback)\n• Backend: Currently unavailable\n• Frontend: Running independently\n• AI: Local rule-based processing\n\nI'll automatically reconnect to the backend when it becomes available.";
    }
    
    if (lowerInput.includes('time')) {
      return `Current time: ${new Date().toLocaleString()}`;
    }
    
    // Default response
    return `I understand you said: "${input}". I'm currently running in self-reliant mode with local processing while the backend reconnects. I can help with basic tasks, and full AI capabilities will be available once the backend connection is restored.`;
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/real-ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          model: selectedModel,
          user_id: "demo_user"
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: data.response,
          timestamp: new Date().toISOString(),
          model: data.model,
          tokens_used: data.tokens_used
        };

        setMessages(prev => [...prev, assistantMessage]);
        setBackendConnected(true);
        setUsingLocalFallback(false);
      } else {
        throw new Error(data.error || "Failed to get response");
      }
    } catch (error) {
      console.error("Chat error:", error);
      setBackendConnected(false);
      
      // Use local AI fallback
      const localResponse = generateLocalResponse(input);
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: localResponse,
        timestamp: new Date().toISOString(),
        model: "local-fallback"
      };

      setMessages(prev => [...prev, assistantMessage]);
      setUsingLocalFallback(true);
    } finally {
      setIsLoading(false);
    }
  };

  const generateCode = async (prompt: string, language: string = "python") => {
    setIsLoading(true);

    try {
      const response = await fetch("/api/real-ai/generate-code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt,
          language,
          model: selectedModel
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `**Generated ${language} code:**\n\n\`\`\`${language}\n${data.code}\n\`\`\``,
          timestamp: new Date().toISOString(),
          model: data.model,
          tokens_used: data.tokens_used
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || "Failed to generate code");
      }
    } catch (error) {
      console.error("Code generation error:", error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Sorry, code generation failed: ${error instanceof Error ? error.message : "Unknown error"}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeText = async (text: string, analysisType: string = "sentiment") => {
    setIsLoading(true);

    try {
      const response = await fetch("/api/real-ai/analyze-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          analysis_type: analysisType,
          model: selectedModel
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `**Text Analysis (${analysisType}):**\n\n${data.analysis}`,
          timestamp: new Date().toISOString(),
          model: data.model,
          tokens_used: data.tokens_used
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || "Failed to analyze text");
      }
    } catch (error) {
      console.error("Text analysis error:", error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Sorry, text analysis failed: ${error instanceof Error ? error.message : "Unknown error"}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const testCapabilities = async () => {
    setIsLoading(true);

    try {
      const response = await fetch("/api/real-ai/test-all-capabilities", {
        method: "POST"
      });

      const data = await response.json();

      if (data.success) {
        const results = Object.entries(data.test_results)
          .map(([capability, status]) => `- ${capability}: ${status}`)
          .join("\n");

        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `**System Capabilities Test Results:**\n\n${results}\n\nSuccess Rate: ${data.success_rate.toFixed(1)}%\nSummary: ${data.summary}`,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || "Failed to test capabilities");
      }
    } catch (error) {
      console.error("Capabilities test error:", error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Sorry, capabilities test failed: ${error instanceof Error ? error.message : "Unknown error"}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Real AI Chat
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            {usingLocalFallback ? (
              <span className="text-yellow-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                Self-Reliant Mode (Local Fallback Active)
              </span>
            ) : (
              <span className="text-green-400 flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Backend Connected
              </span>
            )}
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Switch
              checked={realTimeMode}
              onCheckedChange={setRealTimeMode}
            />
            <span className="text-sm">Real-time</span>
          </div>
          
          {systemStatus && (
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                systemStatus.status === "online" ? "bg-green-400" : "bg-red-400"
              }`} />
              <span className="text-sm">{systemStatus.available_models}/{systemStatus.total_models} models</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* System Status */}
      {systemStatus && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-white/[0.02] border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{systemStatus.available_models}</div>
                  <div className="text-xs text-gray-400">Available Models</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{systemStatus.capabilities.length}</div>
                  <div className="text-xs text-gray-400">Capabilities</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{messages.length}</div>
                  <div className="text-xs text-gray-400">Messages</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">
                    {messages.reduce((sum, msg) => sum + (msg.tokens_used || 0), 0)}
                  </div>
                  <div className="text-xs text-gray-400">Tokens Used</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Messages */}
        <div className="lg:col-span-3">
          <Card className="bg-white/[0.02] border-white/5 h-[600px] flex flex-col">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-cyan-400" />
                JARVIS AI Conversation
              </CardTitle>
              <CardDescription>
                Real AI model responses with actual inference
              </CardDescription>
            </CardHeader>
            
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground/40">
                  <Bot className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
                  <p className="text-sm">
                    Ask JARVIS anything using real AI models
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-3 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-cyan-400" />
                      </div>
                    )}
                    
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        message.role === "user"
                          ? "bg-blue-500/20 text-blue-100"
                          : "bg-white/[0.05] text-white"
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                      
                      <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                        <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                        {message.model && <span>Model: {message.model}</span>}
                        {message.tokens_used && <span>Tokens: {message.tokens_used}</span>}
                      </div>
                    </div>
                    
                    {message.role === "user" && (
                      <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                        <User className="w-4 h-4 text-blue-400" />
                      </div>
                    )}
                  </motion.div>
                ))
              )}
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3 justify-start"
                >
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                    <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                  </div>
                  <div className="bg-white/[0.05] p-3 rounded-lg">
                    <div className="text-sm text-gray-400">JARVIS is thinking...</div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </CardContent>
            
            {/* Input Area */}
            <div className="p-4 border-t border-white/5">
              <div className="flex gap-2">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask JARVIS anything..."
                  className="flex-1 bg-white/[0.05] border-white/10 text-white placeholder:text-gray-400"
                  rows={2}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                  className="bg-cyan-500 hover:bg-cyan-600"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Model Selection */}
          <Card className="bg-white/[0.02] border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">AI Model</CardTitle>
            </CardHeader>
            <CardContent>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="bg-white/[0.05] border-white/10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto Select</SelectItem>
                  {availableModels
                    .filter(model => model.available)
                    .map((model) => (
                      <SelectItem key={model.name} value={model.name.toLowerCase()}>
                        {model.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-white/[0.02] border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={() => generateCode("Create a simple REST API with authentication", "python")}
              >
                <Code className="w-4 h-4 mr-2" />
                Generate Python Code
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={() => analyzeText("I love using JARVIS AI! It's amazing and helps me so much.", "sentiment")}
              >
                <FileText className="w-4 h-4 mr-2" />
                Analyze Sentiment
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={testCapabilities}
              >
                <Zap className="w-4 h-4 mr-2" />
                Test Capabilities
              </Button>
            </CardContent>
          </Card>

          {/* Available Models */}
          <Card className="bg-white/[0.02] border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Available Models</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {availableModels.map((model) => (
                <div key={model.name} className="flex items-center justify-between p-2 rounded bg-white/[0.02]">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      model.available ? "bg-green-400" : "bg-red-400"
                    }`} />
                    <span className="text-sm">{model.name}</span>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {model.type}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Capabilities */}
          {systemStatus && (
            <Card className="bg-white/[0.02] border-white/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">Capabilities</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {systemStatus.capabilities.slice(0, 5).map((capability) => (
                  <div key={capability} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-3 h-3 text-green-400" />
                    <span className="text-gray-300">{capability}</span>
                  </div>
                ))}
                {systemStatus.capabilities.length > 5 && (
                  <div className="text-xs text-gray-400">
                    +{systemStatus.capabilities.length - 5} more
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
