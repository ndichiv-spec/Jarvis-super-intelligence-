'use client';

import { motion } from 'framer-motion';
import { Bot, User, Loader2 } from 'lucide-react';
import type { ChatMessage } from '@/features/chat/types';

interface ChatMessageProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export function ChatMessageBubble({ message, isStreaming }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${
          isUser
            ? 'border-blue-500/30 bg-blue-500/10'
            : 'border-cyan-500/30 bg-cyan-500/10'
        }`}
      >
        {isUser ? (
          <User className="h-4 w-4 text-blue-400" />
        ) : (
          <Bot className="h-4 w-4 text-cyan-400" />
        )}
      </div>

      <div className={`flex max-w-[80%] flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? 'bg-blue-600/20 text-blue-100 border border-blue-500/20'
              : 'bg-white/5 text-gray-100 border border-white/10'
          }`}
        >
          <div className="whitespace-pre-wrap break-words">
            {message.content}
            {isStreaming && (
              <span className="inline-flex ml-1">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-400" />
              </span>
            )}
          </div>
        </div>

        <div className={`flex items-center gap-2 px-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <span className="text-[10px] text-muted-foreground/40">
            {message.timestamp
              ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : ''}
          </span>
          {message.model && !isUser && (
            <span className="rounded-full bg-cyan-500/10 px-2 py-0.5 text-[10px] font-medium text-cyan-400 border border-cyan-500/20">
              {message.model}
            </span>
          )}
          {message.confidence && !isUser && (
            <span className="text-[10px] text-muted-foreground/40">
              {(message.confidence * 100).toFixed(0)}% confidence
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
