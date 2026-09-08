import { create } from 'zustand';
import type { ChatMessage, SessionInfo, ChatStreamChunk } from './types';
import chatApi from './api';
import wsClient from '@/lib/websocket-client';
import API_ENDPOINTS from '@/config/api';

interface ChatState {
  messages: ChatMessage[];
  sessions: SessionInfo[];
  currentSessionId: string | null;
  activeModel: string;
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;
  error: string | null;

  sendMessage: (content: string) => Promise<void>;
  sendStreamMessage: (content: string) => Promise<void>;
  loadSessions: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  newSession: () => void;
  switchModel: (model: string) => Promise<void>;
  setActiveModel: (model: string) => void;
  clearChat: () => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessions: [],
  currentSessionId: null,
  activeModel: 'auto',
  isLoading: false,
  isStreaming: false,
  streamingContent: '',
  error: null,

  sendMessage: async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await chatApi.sendMessage({
        message: content.trim(),
        session_id: get().currentSessionId,
        model: get().activeModel,
      });

      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: response.response || response.content || response.answer || response.reply || '',
        timestamp: response.timestamp || new Date().toISOString(),
        model: response.model,
        confidence: response.confidence,
        sources: response.sources,
        tool_calls: response.tool_calls,
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        currentSessionId: response.session_id || state.currentSessionId,
        isLoading: false,
      }));

      get().loadSessions();
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send message',
      });
    }
  },

  sendStreamMessage: async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    const assistantId = `msg-${Date.now() + 1}`;
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage, assistantMessage],
      isStreaming: true,
      streamingContent: '',
      error: null,
    }));

    await chatApi.sendStreamingMessage(
      { message: content.trim(), session_id: get().currentSessionId, stream: true },
      (chunk: ChatStreamChunk) => {
        if (chunk.type === 'meta' && chunk.session_id) {
          set({ currentSessionId: chunk.session_id });
        } else if (chunk.type === 'chunk' && chunk.text) {
          set((state) => ({
            streamingContent: state.streamingContent + (chunk.text || ''),
            messages: state.messages.map((msg) =>
              msg.id === assistantId
                ? { ...msg, content: state.streamingContent + (chunk.text || '') }
                : msg
            ),
          }));
        } else if (chunk.type === 'complete' || chunk.type === 'done') {
          set((state) => {
            const finalContent = chunk.content || state.streamingContent;
            return {
              isStreaming: false,
              streamingContent: '',
              messages: state.messages.map((msg) =>
                msg.id === assistantId
                  ? {
                      ...msg,
                      content: finalContent,
                      confidence: chunk.confidence,
                      sources: chunk.sources,
                      tool_calls: chunk.tool_calls,
                    }
                  : msg
              ),
            };
          });
          get().loadSessions();
        } else if (chunk.type === 'error') {
          set({ isStreaming: false, error: chunk.error || 'Stream error' });
        }
      },
      (error: Error) => {
        set({ isStreaming: false, error: error.message });
      },
      () => {
        set({ isStreaming: false });
      }
    );
  },

  loadSessions: async () => {
    try {
      const sessions = await chatApi.getSessions();
      set({ sessions });
    } catch {
      // silently fail session loading
    }
  },

  loadSession: async (sessionId: string) => {
    try {
      set({ isLoading: true });
      const data = await chatApi.getSessionHistory(sessionId);
      const messages = (data.messages || []).map((msg) => ({
        id: `msg-${Date.now()}-${Math.random()}`,
        role: (msg.role || 'assistant') as 'user' | 'assistant' | 'system',
        content: msg.content || msg.response || msg.answer || '',
        timestamp: msg.timestamp,
        model: msg.model,
      }));
      set({ messages, currentSessionId: sessionId, isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load session',
      });
    }
  },

  deleteSession: async (sessionId: string) => {
    try {
      await chatApi.deleteSession(sessionId);
      const { currentSessionId } = get();
      if (currentSessionId === sessionId) {
        set({ messages: [], currentSessionId: null });
      }
      get().loadSessions();
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to delete session' });
    }
  },

  newSession: () => {
    set({ messages: [], currentSessionId: null, streamingContent: '' });
  },

  switchModel: async (model: string) => {
    try {
      const result = await chatApi.switchModel(model);
      set({ activeModel: result.active_model });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to switch model' });
    }
  },

  setActiveModel: (model: string) => set({ activeModel: model }),

  clearChat: () => set({ messages: [], streamingContent: '' }),

  clearError: () => set({ error: null }),
}));

export default useChatStore;
