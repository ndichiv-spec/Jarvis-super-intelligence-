'use client';

import { useEffect, useCallback } from 'react';
import wsClient, { type WsEvent, type WsEventType } from '@/lib/websocket-client';

export function useWebSocketSubscription(
  endpoint: string,
  eventTypes: WsEventType[],
  handler: (event: WsEvent) => void,
  deps: unknown[] = []
) {
  const eventSet = new Set(eventTypes);

  const listener = useCallback((event: WsEvent) => {
    if (eventSet.has(event.type)) {
      handler(event);
    }
  }, deps);

  useEffect(() => {
    const unsubscribe = wsClient.subscribe(endpoint, listener);
    return unsubscribe;
  }, [endpoint, listener]);

  return {
    send: (data: unknown) => wsClient.send(endpoint, data),
    isConnected: wsClient.isConnected(endpoint),
    connectionState: wsClient.connectionState(endpoint),
  };
}

export function useHealthWebSocket(onHealthUpdate: (data: any) => void) {
  return useWebSocketSubscription(
    'ws://localhost:8000/ws/health',
    ['health_update'],
    (event) => onHealthUpdate(event.data),
    [onHealthUpdate]
  );
}

export function useAgentWebSocket(onAgentUpdate: (data: any) => void) {
  return useWebSocketSubscription(
    'ws://localhost:8000/ws/agents',
    ['agent_status', 'agent_update'],
    (event) => onAgentUpdate(event.data),
    [onAgentUpdate]
  );
}

export function useMonitoringWebSocket(onMonitoringUpdate: (data: any) => void) {
  return useWebSocketSubscription(
    'ws://localhost:8000/ws/monitoring',
    ['monitoring_update', 'health_update', 'system_alert'],
    (event) => onMonitoringUpdate(event.data),
    [onMonitoringUpdate]
  );
}

export { wsClient } from '@/lib/websocket-client';
