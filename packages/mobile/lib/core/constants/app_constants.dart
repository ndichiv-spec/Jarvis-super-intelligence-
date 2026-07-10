class AppConstants {
  AppConstants._();

  static const String appName = 'JARVIS Mobile';
  static const String appVersion = '1.0.0';
  static const String appBuild = '1';

  static const int sessionTimeoutMinutes = 30;
  static const int heartbeatIntervalSeconds = 30;
  static const int reconnectDelayMs = 3000;
  static const int maxReconnectAttempts = 5;
  static const int cacheSizeLimit = 100;
  static const int pageSize = 20;

  static const String prefSessionId = 'session_id';
  static const String prefWorkspaceId = 'workspace_id';
  static const String prefOrganizationId = 'organization_id';
  static const String prefSubjectId = 'subject_id';
  static const String prefTheme = 'theme_mode';
  static const String prefLocale = 'locale';
  static const String prefBiometricEnabled = 'biometric_enabled';
  static const String prefOfflineMode = 'offline_mode';
  static const String prefNotificationsEnabled = 'notifications_enabled';
}
