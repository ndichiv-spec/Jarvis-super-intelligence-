class ApiConstants {
  ApiConstants._();

  static const String defaultBaseUrl = 'https://api.jarvis.ai';
  static const String apiVersion = '1.0.0';

  static const String healthEndpoint = '/health';
  static const String statsEndpoint = '/stats';
  static const String gatewayPrefix = '/gateway';
  static const String streamPrefix = '/gateway/stream';
  static const String wsPrefix = '/gateway/ws';

  static const String headerApiVersion = 'x-api-version';
  static const String headerSubjectId = 'x-subject-id';
  static const String headerWorkspaceId = 'x-workspace-id';
  static const String headerOrganizationId = 'x-organization-id';
  static const String headerExtensionId = 'x-extension-id';
  static const String headerSessionId = 'x-session-id';
  static const String headerRequestId = 'x-jarvis-request-id';

  static const String subsystemBrain = 'brain';
  static const String subsystemMemory = 'memory';
  static const String subsystemKnowledge = 'knowledge';
  static const String subsystemAgents = 'agents';
  static const String subsystemTools = 'tools';
  static const String subsystemAutomation = 'automation';
  static const String subsystemExtensions = 'extensions';
  static const String subsystemAdministration = 'administration';
}
