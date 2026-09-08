'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { Bot, Loader2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessageBubble } from './chat-message';
import { ChatInput } from './chat-input';
import { SessionList } from './session-list';
import { useChatStore } from '@/features/chat/store';
import type { ChatMessage } from '@/features/chat/types';

interface ChatWindowProps {
  className?: string;
  showSidebar?: boolean;
  onVoiceClick?: () => void;
}

export function ChatWindow({ className = '', showSidebar = true, onVoiceClick }: ChatWindowProps) {
  const {
    messages,
    sessions,
    currentSessionId,
    isLoading,
    isStreaming,
    streamingContent,
    activeModel,
    sendMessage,
    sendStreamMessage,
    loadSessions,
    loadSession,
    deleteSession,
    newSession,
    switchModel,
    error,
    clearError,
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [useStreaming, setUseStreaming] = useState(true);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleSend = useCallback(
    (content: string) => {
      if (useStreaming) {
        sendStreamMessage(content);
      } else {
        sendMessage(content);
      }
    },
    [sendMessage, sendStreamMessage, useStreaming]
  );

  // Show streaming content as a temporary message
  const displayMessages: ChatMessage[] = isStreaming && streamingContent
    ? [
        ...messages,
        {
          id: 'streaming',
          role: 'assistant',
          content: streamingContent,
          timestamp: new Date().toISOString(),
          model: activeModel,
        },
      ]
    : messages;

  return (
    <div className={`flex h-full gap-0 ${className}`}>
      {/* Session Sidebar */}
      {showSidebar && (
        <div className="hidden w-64 shrink-0 border-r border-white/5 bg-white/[0.02] p-3 lg:flex lg:flex-col">
          <SessionList
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelect={loadSession}
            onDelete={deleteSession}
            onNew={newSession}
          />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex flex-1 flex-col">
        {/* Model Selector Bar */}
        <div className="flex items-center justify-between border-b border-white/5 px-4 py-2">
          <div className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-cyan-400" />
            <span className="text-xs font-medium text-muted-foreground/60">
              Active Model:
            </span>
            <select
              value={activeModel}
              onChange={(e) => switchModel(e.target.value)}
              className="rounded-lg border border-white/10 bg-white/[0.03] px-2 py-1 text-xs text-foreground outline-none focus:border-blue-500/40"
            >
              <option value="auto">Auto-Select</option>
              <option value="claude">Claude</option>
              <option value="openai">GPT-4o</option>
              <option value="gemini">Gemini Pro</option>
              <option value="ollama">Local LLM</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-xs text-muted-foreground/50">
            <input
              type="checkbox"
              checked={useStreaming}
              onChange={(e) => setUseStreaming(e.target.checked)}
              className="rounded border-white/20 bg-white/5"
            />
            Stream
          </label>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 px-4 py-4">
          {displayMessages.length === 0 && !isLoading ? (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/10">
                <Bot className="h-8 w-8 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  How can I help you today?
                </h3>
                <p className="mt-1 text-sm text-muted-foreground/50">
                  Ask me anything or give me a task to accomplish
                </p>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex max-w-3xl flex-col gap-4">
              {displayMessages.map((message, index) => (
                <ChatMessageBubble
                  key={message.id || index}
                  message={message}
                  isStreaming={isStreaming && message.id === 'streaming'}
                />
              ))}
            </div>
          )}

          {isLoading && !isStreaming && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
            </div>
          )}

          {error && (
            <div className="mx-auto mt-4 max-w-3xl rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {error}
              <button
                onClick={clearError}
                className="ml-2 underline opacity-70 hover:opacity-100"
              >
                Dismiss
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </ScrollArea>

        {/* Input */}
        <div className="border-t border-white/5 p-4">
          <div className="mx-auto max-w-3xl">
            <ChatInput
              onSend={handleSend}
              onStartVoice={onVoiceClick}
              disabled={isLoading}
              isStreaming={isStreaming}
              onStopStreaming={() => useChatStore.getState().setStreaming(false)}
            />
            <p className="mt-2 text-center text-[10px] text-muted-foreground/30">
              JARVIS may produce inaccurate information. Verify critical facts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
