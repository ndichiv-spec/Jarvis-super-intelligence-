import env from './env';

const API_PREFIX = '/api/v1';

export const API_ENDPOINTS = {
  health: `${env.API_URL}/health`,

  auth: {
    login: `${env.API_URL}${API_PREFIX}/auth/login`,
    register: `${env.API_URL}${API_PREFIX}/auth/register`,
    logout: `${env.API_URL}${API_PREFIX}/auth/logout`,
    me: `${env.API_URL}${API_PREFIX}/auth/me`,
    forgotPassword: `${env.API_URL}${API_PREFIX}/auth/forgot-password`,
    resetPassword: `${env.API_URL}${API_PREFIX}/auth/reset-password`,
    changePassword: `${env.API_URL}${API_PREFIX}/auth/change-password`,
    sessions: `${env.API_URL}${API_PREFIX}/auth/sessions`,
    apiKeys: `${env.API_URL}${API_PREFIX}/auth/api-keys`,
  },

  chat: {
    send: `${env.API_URL}${API_PREFIX}/ai/process`,
    stream: `${env.API_URL}${API_PREFIX}/ai/process`,
    generate: `${env.API_URL}${API_PREFIX}/ai/generate`,
    feedback: `${env.API_URL}${API_PREFIX}/ai/feedback`,
    status: `${env.API_URL}${API_PREFIX}/ai/status`,
    sessions: `${env.API_URL}/api/chat/sessions`,
    history: (sessionId: string) => `${env.API_URL}/api/chat/history/${sessionId}`,
    switchModel: `${env.API_URL}/api/chat/switch`,
  },

  agents: {
    list: `${env.API_URL}${API_PREFIX}/agents`,
    task: `${env.API_URL}${API_PREFIX}/agents/task`,
    tasks: `${env.API_URL}${API_PREFIX}/agents/tasks`,
    stats: `${env.API_URL}${API_PREFIX}/agents/stats`,
    scheduler: `${env.API_URL}${API_PREFIX}/agents/scheduler/status`,
    schedulerToggle: `${env.API_URL}${API_PREFIX}/agents/scheduler/toggle`,
    executions: `${env.API_URL}${API_PREFIX}/agents/executions`,
    collaboration: {
      agents: `${env.API_URL}${API_PREFIX}/agents/collaboration/agents/list`,
      tasks: `${env.API_URL}${API_PREFIX}/agents/collaboration/tasks/list`,
      create: `${env.API_URL}${API_PREFIX}/agents/collaboration/task/create`,
      execute: `${env.API_URL}${API_PREFIX}/agents/collaboration/task/execute`,
      metrics: `${env.API_URL}${API_PREFIX}/agents/collaboration/metrics`,
      selfOrganize: `${env.API_URL}${API_PREFIX}/agents/collaboration/self-organize`,
    },
    serviceTailoring: `${env.API_URL}${API_PREFIX}/agents/service-tailoring`,
  },

  monitoring: {
    healthReport: `${env.API_URL}${API_PREFIX}/monitoring/health-report`,
    metrics: `${env.API_URL}${API_PREFIX}/monitoring/metrics`,
    optimizationReport: `${env.API_URL}${API_PREFIX}/monitoring/optimization-report`,
    optimize: `${env.API_URL}${API_PREFIX}/monitoring/optimize`,
    diagnostics: `${env.API_URL}${API_PREFIX}/monitoring/system/diagnostics`,
    recoveryHistory: `${env.API_URL}${API_PREFIX}/monitoring/recovery-history`,
    triggerRecovery: `${env.API_URL}${API_PREFIX}/monitoring/trigger-recovery`,
  },

  system: {
    status: `${env.API_URL}${API_PREFIX}/system/status`,
    capabilities: `${env.API_URL}${API_PREFIX}/system/capabilities`,
    processes: `${env.API_URL}${API_PREFIX}/system/processes`,
    providerSettings: `${env.API_URL}${API_PREFIX}/system/provider-settings`,
    files: `${env.API_URL}${API_PREFIX}/system/files`,
  },

  voice: {
    speak: `${env.API_URL}${API_PREFIX}/voice/speak`,
    listen: `${env.API_URL}${API_PREFIX}/voice/listen`,
    transcribe: `${env.API_URL}${API_PREFIX}/voice/transcribe`,
    profiles: `${env.API_URL}${API_PREFIX}/voice/profile`,
    voices: `${env.API_URL}${API_PREFIX}/voice/voices`,
    status: `${env.API_URL}${API_PREFIX}/voice/status`,
  },

  memory: {
    store: `${env.API_URL}${API_PREFIX}/cognitive/memory/store`,
    recall: `${env.API_URL}${API_PREFIX}/cognitive/memory/recall`,
    stats: `${env.API_URL}${API_PREFIX}/cognitive/memory/stats`,
    consolidate: `${env.API_URL}${API_PREFIX}/cognitive/memory/consolidate`,
    cognitiveReport: `${env.API_URL}${API_PREFIX}/cognitive/consciousness/report`,
    cognitiveProcess: `${env.API_URL}${API_PREFIX}/cognitive/process`,
    emotionAnalyze: `${env.API_URL}${API_PREFIX}/cognitive/emotion/analyze`,
    knowledgeGraph: `${env.API_URL}${API_PREFIX}/cognitive/knowledge/search`,
  },

  automation: {
    tasks: `${env.API_URL}${API_PREFIX}/automation`,
    runTask: (taskId: string) => `${env.API_URL}${API_PREFIX}/automation/task/${taskId}/run`,
  },

  knowledge: {
    search: `${env.API_URL}${API_PREFIX}/knowledge/search`,
    entries: `${env.API_URL}${API_PREFIX}/knowledge`,
    patterns: `${env.API_URL}${API_PREFIX}/knowledge/patterns`,
  },

  stark: {
    chat: `${env.API_URL}${API_PREFIX}/stark/chat`,
    tool: `${env.API_URL}${API_PREFIX}/stark/tool`,
    status: `${env.API_URL}${API_PREFIX}/stark/status`,
    health: `${env.API_URL}${API_PREFIX}/stark/health`,
  },

  global: {
    knowledgeSearch: `${env.API_URL}${API_PREFIX}/global/knowledge/global/search`,
    trends: `${env.API_URL}${API_PREFIX}/global/knowledge/global/trends`,
    codeSearch: `${env.API_URL}${API_PREFIX}/global/knowledge/global/code`,
    sources: `${env.API_URL}${API_PREFIX}/global/knowledge/global/sources`,
    observationStatus: `${env.API_URL}${API_PREFIX}/global/observation/status`,
    observationReport: `${env.API_URL}${API_PREFIX}/global/observation/report`,
    observationEvents: `${env.API_URL}${API_PREFIX}/global/observation/events`,
    observationMetrics: `${env.API_URL}${API_PREFIX}/global/observation/metrics`,
    rssFeeds: `${env.API_URL}${API_PREFIX}/global/rss/feeds`,
    rssLatest: `${env.API_URL}${API_PREFIX}/global/rss/latest`,
    rssRefresh: `${env.API_URL}${API_PREFIX}/global/rss/refresh`,
  },

  rbac: {
    users: `${env.API_URL}${API_PREFIX}/rbac/users`,
    roles: `${env.API_URL}${API_PREFIX}/rbac/roles`,
    permissions: `${env.API_URL}${API_PREFIX}/rbac/permissions`,
    auditLogs: `${env.API_URL}${API_PREFIX}/rbac/audit-logs`,
    tenantSettings: `${env.API_URL}${API_PREFIX}/rbac/tenant/settings`,
  },

  llm: {
    chat: `${env.API_URL}${API_PREFIX}/llm/chat`,
    status: `${env.API_URL}${API_PREFIX}/llm/status`,
  },

  ws: {
    chat: `${env.WS_URL}/ws/chat`,
    health: `${env.WS_URL}/ws/health`,
    agents: `${env.WS_URL}/ws/agents`,
    voice: `${env.WS_URL}/api/v1/voice/ws/chat`,
    stark: `${env.WS_URL}/api/v1/stark/ws/chat`,
    monitoring: `${env.WS_URL}/ws/monitoring`,
  },
};

export default API_ENDPOINTS;
