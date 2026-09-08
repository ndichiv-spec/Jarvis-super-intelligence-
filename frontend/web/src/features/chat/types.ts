export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  model?: string;
  tool_calls?: ToolCall[];
  sources?: string[];
  confidence?: number;
  skill_used?: string;
  metadata?: Record<string, unknown>;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result?: unknown;
  status?: 'pending' | 'running' | 'completed' | 'failed';
}

export interface ChatResponse {
  success: boolean;
  response?: string;
  content?: string;
  answer?: string;
  reply?: string;
  session_id?: string;
  message?: string;
  model?: string;
  confidence?: number;
  sources?: string[];
  intent?: string;
  processing_time?: number;
  timestamp?: string;
  tool_calls?: ToolCall[];
  tool_results?: unknown[];
}

export interface SessionInfo {
  session_id: string;
  preview: string;
  started: string;
  last_active?: string;
  message_count?: number;
  model?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string | null;
  stream?: boolean;
  model?: string;
}

export interface ChatStreamChunk {
  type: 'meta' | 'chunk' | 'done' | 'error' | 'typing' | 'complete';
  session_id?: string;
  text?: string;
  content?: string;
  confidence?: number;
  sources?: string[];
  tool_calls?: ToolCall[];
  error?: string;
}

export const CHAT_MODELS = [
  { id: 'claude', name: 'Claude', provider: 'Anthropic' },
  { id: 'openai', name: 'GPT-4o', provider: 'OpenAI' },
  { id: 'gemini', name: 'Gemini Pro', provider: 'Google' },
  { id: 'ollama', name: 'Local LLM', provider: 'Ollama' },
  { id: 'auto', name: 'Auto-Select', provider: 'JARVIS' },
] as const;

export type ChatModelId = typeof CHAT_MODELS[number]['id'];
