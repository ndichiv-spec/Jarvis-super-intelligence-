class GatewayPaths {
  GatewayPaths._();

  static const String authLogin = '/auth/login';
  static const String authLogout = '/auth/logout';
  static const String authRefresh = '/auth/refresh';
  static const String authBiometric = '/auth/biometric';

  static const String workspaceCurrent = '/workspace/current';
  static const String workspaceList = '/workspace/list';

  static const String conversationList = '/brain/conversations';
  static const String conversationCreate = '/brain/conversations';
  static const String conversationStream = '/brain/conversations/stream';
  static const String conversationMessages = '/brain/conversations/';

  static const String projectList = '/brain/projects';
  static const String projectDetail = '/brain/projects/';

  static const String memoryList = '/memory/items';
  static const String memorySearch = '/memory/search';
  static const String memoryArchive = '/memory/archive';

  static const String knowledgeSearch = '/knowledge/search';
  static const String knowledgeDocument = '/knowledge/documents/';
  static const String knowledgeCollections = '/knowledge/collections';

  static const String automationList = '/automation/workflows';
  static const String automationDetail = '/automation/workflows/';
  static const String automationHistory = '/automation/history';
  static const String automationAction = '/automation/workflows/action';

  static const String notificationList = '/notifications';
  static const String notificationMarkRead = '/notifications/read';
  static const String notificationSettings = '/notifications/settings';

  static const String sessionList = '/administration/sessions';
  static const String sessionRevoke = '/administration/sessions/revoke';

  static const String deviceRegister = '/administration/devices/register';
  static const String deviceList = '/administration/devices';

  static const String settingsGet = '/administration/settings';
  static const String settingsUpdate = '/administration/settings';

  static const String diagnosticsHealth = '/health';
  static const String diagnosticsStats = '/stats';
  static const String quickActions = '/administration/quick-actions';
}
