"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";

interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

type Fetcher<T> = () => Promise<T>;

export function useApi<T>(fetcher: Fetcher<T>, immediate = true) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    isLoading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState((s) => ({ ...s, isLoading: true, error: null }));
    try {
      const data = await fetcher();
      setState({ data, isLoading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : "An error occurred";
      setState((s) => ({ ...s, isLoading: false, error }));
      throw err;
    }
  }, [fetcher]);

  const reset = useCallback(() => {
    setState({ data: null, isLoading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}

export function useDashboardStats() {
  return useApi(() => api.dashboard.stats());
}

export function useConversations() {
  return useApi(() => api.conversations.list());
}

export function useProjects() {
  return useApi(() => api.projects.list());
}

export function useMemories() {
  return useApi(() => api.memory.list());
}

export function useKnowledgeDocuments() {
  return useApi(() => api.knowledge.search(""));
}

export function useAutomations() {
  return useApi(() => api.automations.list());
}

export function useAgents() {
  return useApi(() => api.agents.list());
}

export function useTools() {
  return useApi(() => api.tools.list());
}

export function useExtensions() {
  return useApi(() => api.extensions.list());
}

export function useNotifications() {
  return useApi(() => api.notifications.list());
}

export function useProfile() {
  return useApi(() => api.profile.get());
}
