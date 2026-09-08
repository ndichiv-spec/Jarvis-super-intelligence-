import apiClient from '@/lib/api-client';
import API_ENDPOINTS from '@/config/api';
import type { ChatResponse, ChatRequest, SessionInfo, ChatStreamChunk } from './types';

export const chatApi = {
  sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>(API_ENDPOINTS.chat.send, {
      input: request.message,
      mode: 'chat',
      model: request.model || 'auto',
      stream: request.stream || false,
      session_id: request.session_id,
    });
  },

  async sendStreamingMessage(
    request: ChatRequest,
    onChunk: (chunk: ChatStreamChunk) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): Promise<void> {
    try {
      const response = await fetch(API_ENDPOINTS.chat.stream, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: request.message,
          session_id: request.session_id,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Stream request failed: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body reader available');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const chunk = JSON.parse(line.slice(6)) as ChatStreamChunk;
              onChunk(chunk);
            } catch {
              // skip malformed chunks
            }
          }
        }
      }

      if (buffer.startsWith('data: ')) {
        try {
          onChunk(JSON.parse(buffer.slice(6)) as ChatStreamChunk);
        } catch {
          // skip
        }
      }

      onComplete();
    } catch (error) {
      onError(error instanceof Error ? error : new Error(String(error)));
    }
  },

  getSessions(): Promise<SessionInfo[]> {
    return apiClient.get<SessionInfo[]>(API_ENDPOINTS.chat.sessions);
  },

  getSessionHistory(sessionId: string): Promise<{ messages: ChatResponse[] }> {
    return apiClient.get<{ messages: ChatResponse[] }>(API_ENDPOINTS.chat.history(sessionId));
  },

  deleteSession(sessionId: string): Promise<{ success: boolean }> {
    return apiClient.delete<{ success: boolean }>(API_ENDPOINTS.chat.history(sessionId));
  },

  switchModel(model: string): Promise<{ active_model: string }> {
    return apiClient.post<{ active_model: string }>(API_ENDPOINTS.chat.switchModel, { model });
  },

  sendFeedback(query: string, response: string, rating: number): Promise<{ success: boolean }> {
    return apiClient.post<{ success: boolean }>(API_ENDPOINTS.chat.feedback, { query, response, rating });
  },

  getStatus(): Promise<{ status: string; model: string }> {
    return apiClient.get<{ status: string; model: string }>(API_ENDPOINTS.chat.status);
  },
};

export default chatApi;
