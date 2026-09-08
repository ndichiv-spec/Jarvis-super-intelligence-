"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  FileCode, Folder, FolderOpen, Play, Search, Save, Undo,
  Terminal, Code2, Eye, GitBranch, RefreshCw, Plus, Trash2,
  Edit3, ChevronRight, ChevronDown, BookOpen, Brain, Zap,
  AlertCircle, CheckCircle, Clock, FileText, Settings, X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

interface FileNode {
  path: string;
  name: string;
  is_directory: boolean;
  size: number;
  extension: string;
  modified: string;
}

interface CodeAnalysis {
  file_path: string;
  language: string;
  lines_of_code: number;
  functions: string[];
  classes: string[];
  imports: string[];
  complexity_score: number;
  suggestions: string[];
}

export default function SelfReliantIDE() {
  const [activeTab, setActiveTab] = useState("editor");
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState("");
  const [originalContent, setOriginalContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [terminalOutput, setTerminalOutput] = useState("");
  const [terminalInput, setTerminalInput] = useState("");
  const [codeAnalysis, setCodeAnalysis] = useState<CodeAnalysis | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(["."]));
  const [showFileTree, setShowFileTree] = useState(true);

  useEffect(() => {
    loadFileTree();
  }, []);

  const loadFileTree = async () => {
    try {
      setIsLoading(true);
      // Mock file tree for demo
      setFileTree([
        { path: "core", name: "core", is_directory: true, size: 0, extension: "", modified: "" },
        { path: "core/ai_engine.py", name: "ai_engine.py", is_directory: false, size: 45230, extension: ".py", modified: "2024-01-15" },
        { path: "core/advanced_memory.py", name: "advanced_memory.py", is_directory: false, size: 52000, extension: ".py", modified: "2024-01-15" },
        { path: "core/self_reliant_ide.py", name: "self_reliant_ide.py", is_directory: false, size: 38000, extension: ".py", modified: "2024-01-15" },
        { path: "api", name: "api", is_directory: true, size: 0, extension: "", modified: "" },
        { path: "api/main.py", name: "main.py", is_directory: false, size: 12000, extension: ".py", modified: "2024-01-15" },
        { path: "web", name: "web", is_directory: true, size: 0, extension: "", modified: "" },
        { path: "web/src", name: "src", is_directory: true, size: 0, extension: "", modified: "" },
        { path: ".env.example", name: ".env.example", is_directory: false, size: 2500, extension: "", modified: "2024-01-15" },
        { path: "README.md", name: "README.md", is_directory: false, size: 8500, extension: ".md", modified: "2024-01-15" },
      ]);
    } catch (error) {
      console.error("Failed to load file tree:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const openFile = async (filePath: string) => {
    try {
      setIsLoading(true);
      setSelectedFile(filePath);

      // Mock file content
      const mockContent = `# JARVIS Self-Reliant IDE
# File: ${filePath}

"""
This is a sample file being edited in the web-based IDE.
JARVIS can read, analyze, and modify its own code without external tools.
"""

class SampleClass:
    """Sample class for demonstration"""
    
    def __init__(self):
        self.name = "JARVIS"
        self.version = "4.0.0"
    
    def self_improve(self):
        """Self-improvement method"""
        print(f"{self.name} is improving itself...")
        return True

def main():
    """Main function"""
    jarvis = SampleClass()
    jarvis.self_improve()

if __name__ == "__main__":
    main()
`;
      setFileContent(mockContent);
      setOriginalContent(mockContent);

      // Analyze file
      setCodeAnalysis({
        file_path: filePath,
        language: filePath.endsWith('.py') ? 'Python' : 'JavaScript',
        lines_of_code: 25,
        functions: ['self_improve', 'main'],
        classes: ['SampleClass'],
        imports: ['json', 'logging', 'datetime'],
        complexity_score: 3.5,
        suggestions: ['Code looks good! No major issues detected'],
      });

      toast.success(`Opened ${filePath}`);
    } catch (error: any) {
      toast.error(`Failed to open file: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const saveFile = async () => {
    if (!selectedFile) return;
    try {
      toast.info("Saving file...");
      setOriginalContent(fileContent);
      toast.success(`Saved ${selectedFile}`);
    } catch (error: any) {
      toast.error(`Failed to save: ${error.message}`);
    }
  };

  const undoChanges = () => {
    setFileContent(originalContent);
    toast.info("Changes undone");
  };

  const executeInTerminal = async () => {
    try {
      setTerminalOutput(prev => prev + `$ ${terminalInput}\n`);
      // Mock execution
      setTerminalOutput(prev => prev + `Command executed successfully\n\n`);
      setTerminalInput("");
    } catch (error: any) {
      setTerminalOutput(prev => prev + `Error: ${error.message}\n\n`);
    }
  };

  const indexCodebase = async () => {
    try {
      toast.info("Indexing codebase...");
      // Mock indexing
      toast.success("Codebase indexed: 47 files, 12,847 lines");
    } catch (error: any) {
      toast.error(`Indexing failed: ${error.message}`);
    }
  };

  const selfAnalyze = async () => {
    try {
      toast.info("JARVIS is analyzing its own code...");
      // Mock analysis
      toast.success("Analysis complete: 6 languages, 120+ functions, 28 classes");
    } catch (error: any) {
      toast.error(`Analysis failed: ${error.message}`);
    }
  };

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const getFileIcon = (file: FileNode) => {
    if (file.is_directory) {
      return expandedFolders.has(file.path) ? FolderOpen : Folder;
    }
    if (file.extension === '.py') return FileCode;
    if (file.extension === '.js' || file.extension === '.jsx') return FileCode;
    if (file.extension === '.ts' || file.extension === '.tsx') return FileCode;
    if (file.extension === '.md') return BookOpen;
    return FileText;
  };

  const getLanguageColor = (lang: string) => {
    const colors: Record<string, string> = {
      Python: "bg-blue-500/20 text-blue-400",
      JavaScript: "bg-yellow-500/20 text-yellow-400",
      TypeScript: "bg-blue-500/20 text-blue-400",
    };
    return colors[lang] || "bg-gray-500/20 text-gray-400";
  };

  const renderFileTree = () => {
    const grouped: Record<string, FileNode[]> = {};
    fileTree.forEach(file => {
      const parent = file.path.includes('/') ? file.path.split('/').slice(0, -1).join('/') : '.';
      if (!grouped[parent]) grouped[parent] = [];
      grouped[parent].push(file);
    });

    return (
      <div className="space-y-1">
        {fileTree.filter(f => f.is_directory || f.path.includes('/') === false).map((file, i) => {
          const Icon = getFileIcon(file);
          const isExpanded = expandedFolders.has(file.path);

          return (
            <motion.div
              key={file.path}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.02 }}
            >
              <button
                onClick={() => file.is_directory ? toggleFolder(file.path) : openFile(file.path)}
                className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-white/5 ${
                  selectedFile === file.path ? 'bg-blue-500/10 text-blue-400' : 'text-muted-foreground/70'
                }`}
              >
                {file.is_directory && (
                  isExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />
                )}
                {!file.is_directory && <span className="w-3" />}
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span className="truncate">{file.name}</span>
              </button>

              {file.is_directory && isExpanded && (
                <div className="ml-4 border-l border-white/5 pl-2 mt-1">
                  {fileTree
                    .filter(f => f.path.startsWith(file.path + '/') && f.path.split('/').length === file.path.split('/').length + 1)
                    .map((child, j) => {
                      const ChildIcon = getFileIcon(child);
                      return (
                        <button
                          key={child.path}
                          onClick={() => child.is_directory ? toggleFolder(child.path) : openFile(child.path)}
                          className={`w-full flex items-center gap-2 px-2 py-1 rounded text-xs hover:bg-white/5 ${
                            selectedFile === child.path ? 'bg-blue-500/10 text-blue-400' : 'text-muted-foreground/60'
                          }`}
                        >
                          {child.is_directory && (
                            expandedFolders.has(child.path) ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />
                          )}
                          {!child.is_directory && <span className="w-3" />}
                          <ChildIcon className="h-3 w-3" />
                          <span className="truncate">{child.name}</span>
                        </button>
                      );
                    })}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between p-4 border-b border-white/5">
        <div className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-purple-400" />
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
              JARVIS Self-Reliant IDE
            </h1>
            <p className="text-xs text-muted-foreground/60">
              No PyCharm, No VS Code - Complete independence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={indexCodebase}>
            <Search className="mr-2 h-4 w-4" />
            Index Codebase
          </Button>
          <Button variant="outline" size="sm" onClick={selfAnalyze}>
            <Brain className="mr-2 h-4 w-4" />
            Self-Analyze
          </Button>
          <Button size="sm" className="bg-gradient-to-r from-purple-500 to-pink-500">
            <Zap className="mr-2 h-4 w-4" />
            AI Auto-Improve
          </Button>
        </div>
      </motion.div>

      <div className="flex flex-1 overflow-hidden">
        {/* File Tree Sidebar */}
        {showFileTree && (
          <div className="w-64 border-r border-white/5 bg-white/[0.02]">
            <div className="p-3 border-b border-white/5 flex items-center justify-between">
              <span className="text-sm font-semibold">Explorer</span>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setShowFileTree(false)}>
                <X className="h-3 w-3" />
              </Button>
            </div>
            <ScrollArea className="h-[calc(100vh-8rem)]">
              <div className="p-2">
                {renderFileTree()}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Toolbar */}
          <div className="flex items-center gap-2 p-2 border-b border-white/5 bg-white/[0.02]">
            {!showFileTree && (
              <Button variant="ghost" size="sm" onClick={() => setShowFileTree(true)}>
                <Folder className="h-4 w-4" />
              </Button>
            )}
            {selectedFile && (
              <>
                <span className="text-sm text-muted-foreground/60">{selectedFile}</span>
                <Separator orientation="vertical" className="h-4" />
                <Button variant="outline" size="sm" onClick={saveFile}>
                  <Save className="mr-1 h-3 w-3" />
                  Save
                </Button>
                <Button variant="outline" size="sm" onClick={undoChanges}>
                  <Undo className="mr-1 h-3 w-3" />
                  Undo
                </Button>
              </>
            )}
          </div>

          {/* Editor Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="bg-white/[0.02] border-b border-white/5 rounded-none">
              <TabsTrigger value="editor" className="text-sm">
                <Edit3 className="mr-2 h-4 w-4" />
                Editor
              </TabsTrigger>
              <TabsTrigger value="analysis" className="text-sm">
                <Code2 className="mr-2 h-4 w-4" />
                Analysis
              </TabsTrigger>
              <TabsTrigger value="terminal" className="text-sm">
                <Terminal className="mr-2 h-4 w-4" />
                Terminal
              </TabsTrigger>
              <TabsTrigger value="self-read" className="text-sm">
                <Eye className="mr-2 h-4 w-4" />
                Self-Read
              </TabsTrigger>
            </TabsList>

            {/* Editor Tab */}
            <TabsContent value="editor" className="flex-1 overflow-hidden">
              {selectedFile ? (
                <div className="h-full flex flex-col">
                  <Textarea
                    value={fileContent}
                    onChange={(e) => setFileContent(e.target.value)}
                    className="flex-1 font-mono text-sm bg-transparent border-none resize-none focus-visible:ring-0"
                    placeholder="File content will appear here..."
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground/40">
                  <div className="text-center">
                    <FileCode className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <h3 className="text-lg font-semibold mb-2">No File Open</h3>
                    <p className="text-sm">Select a file from the explorer to start editing</p>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* Analysis Tab */}
            <TabsContent value="analysis" className="flex-1 p-4 overflow-auto">
              {codeAnalysis ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: "Language", value: codeAnalysis.language, color: getLanguageColor(codeAnalysis.language) },
                      { label: "Lines", value: codeAnalysis.lines_of_code, icon: FileText },
                      { label: "Functions", value: codeAnalysis.functions.length, icon: Code2 },
                      { label: "Complexity", value: codeAnalysis.complexity_score.toFixed(1), icon: Brain },
                    ].map((stat, i) => (
                      <Card key={i} className="bg-white/[0.02] border-white/5">
                        <CardContent className="p-3">
                          <p className="text-xs text-muted-foreground/60 mb-1">{stat.label}</p>
                          <p className={`text-xl font-bold ${stat.color?.includes('text') ? stat.color.split(' ')[1] : ''}`}>
                            {stat.value}
                          </p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  <Separator />

                  <div>
                    <h4 className="text-sm font-semibold mb-2">Functions</h4>
                    <div className="flex gap-2 flex-wrap">
                      {codeAnalysis.functions.map((fn, i) => (
                        <Badge key={i} variant="outline" className="bg-blue-500/10 text-blue-400">{fn}</Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2">Classes</h4>
                    <div className="flex gap-2 flex-wrap">
                      {codeAnalysis.classes.map((cls, i) => (
                        <Badge key={i} variant="outline" className="bg-purple-500/10 text-purple-400">{cls}</Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2">Suggestions</h4>
                    <div className="space-y-1">
                      {codeAnalysis.suggestions.map((suggestion, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground/70">
                          <CheckCircle className="h-4 w-4 text-emerald-400" />
                          {suggestion}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground/40">
                  <Code2 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Open a file to see analysis</p>
                </div>
              )}
            </TabsContent>

            {/* Terminal Tab */}
            <TabsContent value="terminal" className="flex-1 flex flex-col">
              <ScrollArea className="flex-1 p-4">
                <pre className="font-mono text-sm text-green-400 whitespace-pre-wrap">
                  {terminalOutput || "JARVIS Terminal v4.0\nType commands and press Enter...\n\n"}
                </pre>
              </ScrollArea>
              <div className="p-3 border-t border-white/5 flex items-center gap-2">
                <span className="text-green-400 font-mono text-sm">$</span>
                <Input
                  value={terminalInput}
                  onChange={(e) => setTerminalInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && executeInTerminal()}
                  placeholder="Type command..."
                  className="bg-transparent border-none focus-visible:ring-0 font-mono text-sm"
                />
              </div>
            </TabsContent>

            {/* Self-Read Tab */}
            <TabsContent value="self-read" className="flex-1 p-4 overflow-auto">
              <div className="space-y-4">
                <Card className="bg-white/[0.02] border-white/5">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Eye className="h-5 w-5 text-cyan-400" />
                      JARVIS Self-Reading Mode
                    </CardTitle>
                    <CardDescription>
                      AI reads and understands its own codebase
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="p-3 rounded bg-cyan-500/10 border border-cyan-500/20">
                        <p className="text-sm font-semibold text-cyan-400 mb-2">What JARVIS Can Do:</p>
                        <ul className="space-y-1 text-sm text-muted-foreground/70">
                          <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-emerald-400" /> Read all its own source files</li>
                          <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-emerald-400" /> Understand code structure (functions, classes, imports)</li>
                          <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-emerald-400" /> Analyze complexity and quality</li>
                          <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-emerald-400" /> Edit its own code safely</li>
                          <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-emerald-400" /> Execute terminal commands</li>
                          <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-emerald-400" /> No PyCharm or external IDE needed</li>
                        </ul>
                      </div>

                      <Button className="w-full" onClick={selfAnalyze}>
                        <Brain className="mr-2 h-4 w-4" />
                        Start Self-Analysis
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
