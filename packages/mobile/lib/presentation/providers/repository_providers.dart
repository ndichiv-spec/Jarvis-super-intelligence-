import 'package:jarvis_mobile/core/constants/api_constants.dart';
import 'package:jarvis_mobile/core/network/connectivity_service.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/core/network/local_database.dart';
import 'package:jarvis_mobile/core/security/biometric_auth.dart';
import 'package:jarvis_mobile/core/security/secure_storage.dart';
import 'package:jarvis_mobile/data/datasources/auth_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/automation_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/conversation_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/diagnostics_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/knowledge_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/memory_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/notification_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/project_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/quick_action_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/security_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/settings_remote_datasource.dart';
import 'package:jarvis_mobile/data/datasources/workspace_remote_datasource.dart';
import 'package:jarvis_mobile/data/repositories/auth_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/automation_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/conversation_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/diagnostics_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/knowledge_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/memory_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/notification_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/project_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/quick_action_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/security_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/settings_repository_impl.dart';
import 'package:jarvis_mobile/data/repositories/workspace_repository_impl.dart';
import 'package:jarvis_mobile/domain/repositories/auth_repository.dart';
import 'package:jarvis_mobile/domain/repositories/automation_repository.dart';
import 'package:jarvis_mobile/domain/repositories/conversation_repository.dart';
import 'package:jarvis_mobile/domain/repositories/diagnostics_repository.dart';
import 'package:jarvis_mobile/domain/repositories/knowledge_repository.dart';
import 'package:jarvis_mobile/domain/repositories/memory_repository.dart';
import 'package:jarvis_mobile/domain/repositories/notification_repository.dart';
import 'package:jarvis_mobile/domain/repositories/project_repository.dart';
import 'package:jarvis_mobile/domain/repositories/quick_action_repository.dart';
import 'package:jarvis_mobile/domain/repositories/security_repository.dart';
import 'package:jarvis_mobile/domain/repositories/settings_repository.dart';
import 'package:jarvis_mobile/domain/repositories/workspace_repository.dart';
import 'package:jarvis_mobile/domain/usecases/execute_quick_action_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_conversations_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_diagnostics_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_notifications_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_project_details_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_projects_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_settings_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/login_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/logout_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/manage_sessions_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/manage_workflow_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/search_knowledge_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/search_memory_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/send_message_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/stream_conversation_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/update_settings_usecase.dart';
import 'package:riverpod/riverpod.dart';

// ---------------------------------------------------------------------------
// Core services
// ---------------------------------------------------------------------------

final connectivityServiceProvider = Provider<ConnectivityService>((ref) {
  return ConnectivityService();
});

final httpClientProvider = Provider<HttpClient>((ref) {
  return HttpClient(baseUrl: ApiConstants.defaultBaseUrl);
});

final localDatabaseProvider = Provider<LocalDatabase>((ref) {
  return LocalDatabase();
});

final secureStorageProvider = Provider<SecureStorage>((ref) {
  return SecureStorage();
});

final biometricAuthServiceProvider = Provider<BiometricAuth>((ref) {
  return BiometricAuth();
});

// ---------------------------------------------------------------------------
// Remote data sources
// ---------------------------------------------------------------------------

final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  return AuthRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final workspaceRemoteDataSourceProvider = Provider<WorkspaceRemoteDataSource>((ref) {
  return WorkspaceRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final conversationRemoteDataSourceProvider = Provider<ConversationRemoteDataSource>((ref) {
  return ConversationRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final projectRemoteDataSourceProvider = Provider<ProjectRemoteDataSource>((ref) {
  return ProjectRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final memoryRemoteDataSourceProvider = Provider<MemoryRemoteDataSource>((ref) {
  return MemoryRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final knowledgeRemoteDataSourceProvider = Provider<KnowledgeRemoteDataSource>((ref) {
  return KnowledgeRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final automationRemoteDataSourceProvider = Provider<AutomationRemoteDataSource>((ref) {
  return AutomationRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final notificationRemoteDataSourceProvider = Provider<NotificationRemoteDataSource>((ref) {
  return NotificationRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final quickActionRemoteDataSourceProvider = Provider<QuickActionRemoteDataSource>((ref) {
  return QuickActionRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final securityRemoteDataSourceProvider = Provider<SecurityRemoteDataSource>((ref) {
  return SecurityRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final settingsRemoteDataSourceProvider = Provider<SettingsRemoteDataSource>((ref) {
  return SettingsRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

final diagnosticsRemoteDataSourceProvider = Provider<DiagnosticsRemoteDataSource>((ref) {
  return DiagnosticsRemoteDataSource(httpClient: ref.watch(httpClientProvider));
});

// ---------------------------------------------------------------------------
// Repositories
// ---------------------------------------------------------------------------

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(remoteDataSource: ref.watch(authRemoteDataSourceProvider));
});

final workspaceRepositoryProvider = Provider<WorkspaceRepository>((ref) {
  return WorkspaceRepositoryImpl(remoteDataSource: ref.watch(workspaceRemoteDataSourceProvider));
});

final conversationRepositoryProvider = Provider<ConversationRepository>((ref) {
  return ConversationRepositoryImpl(
    remoteDataSource: ref.watch(conversationRemoteDataSourceProvider),
    httpClient: ref.watch(httpClientProvider),
  );
});

final projectRepositoryProvider = Provider<ProjectRepository>((ref) {
  return ProjectRepositoryImpl(remoteDataSource: ref.watch(projectRemoteDataSourceProvider));
});

final memoryRepositoryProvider = Provider<MemoryRepository>((ref) {
  return MemoryRepositoryImpl(remoteDataSource: ref.watch(memoryRemoteDataSourceProvider));
});

final knowledgeRepositoryProvider = Provider<KnowledgeRepository>((ref) {
  return KnowledgeRepositoryImpl(remoteDataSource: ref.watch(knowledgeRemoteDataSourceProvider));
});

final automationRepositoryProvider = Provider<AutomationRepository>((ref) {
  return AutomationRepositoryImpl(remoteDataSource: ref.watch(automationRemoteDataSourceProvider));
});

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepositoryImpl(remoteDataSource: ref.watch(notificationRemoteDataSourceProvider));
});

final quickActionRepositoryProvider = Provider<QuickActionRepository>((ref) {
  return QuickActionRepositoryImpl(remoteDataSource: ref.watch(quickActionRemoteDataSourceProvider));
});

final securityRepositoryProvider = Provider<SecurityRepository>((ref) {
  return SecurityRepositoryImpl(remoteDataSource: ref.watch(securityRemoteDataSourceProvider));
});

final settingsRepositoryProvider = Provider<SettingsRepository>((ref) {
  return SettingsRepositoryImpl(remoteDataSource: ref.watch(settingsRemoteDataSourceProvider));
});

final diagnosticsRepositoryProvider = Provider<DiagnosticsRepository>((ref) {
  return DiagnosticsRepositoryImpl(
    remoteDataSource: ref.watch(diagnosticsRemoteDataSourceProvider),
    connectivityService: ref.watch(connectivityServiceProvider),
    localDatabase: ref.watch(localDatabaseProvider),
  );
});

// ---------------------------------------------------------------------------
// Use cases
// ---------------------------------------------------------------------------

final loginUseCaseProvider = Provider<LoginUseCase>((ref) {
  return LoginUseCase(ref.watch(authRepositoryProvider));
});

final logoutUseCaseProvider = Provider<LogoutUseCase>((ref) {
  return LogoutUseCase(ref.watch(authRepositoryProvider));
});

final getConversationsUseCaseProvider = Provider<GetConversationsUseCase>((ref) {
  return GetConversationsUseCase(ref.watch(conversationRepositoryProvider));
});

final sendMessageUseCaseProvider = Provider<SendMessageUseCase>((ref) {
  final repo = ref.watch(conversationRepositoryProvider);
  return _ConversationSendMessageUseCase(repo);
});

final streamConversationUseCaseProvider = Provider<StreamConversationUseCase>((ref) {
  return StreamConversationUseCase(ref.watch(conversationRepositoryProvider));
});

final getProjectsUseCaseProvider = Provider<GetProjectsUseCase>((ref) {
  return GetProjectsUseCase(ref.watch(projectRepositoryProvider));
});

final getProjectDetailsUseCaseProvider = Provider<GetProjectDetailsUseCase>((ref) {
  return GetProjectDetailsUseCase(ref.watch(projectRepositoryProvider));
});

final searchMemoryUseCaseProvider = Provider<SearchMemoryUseCase>((ref) {
  return SearchMemoryUseCase(ref.watch(memoryRepositoryProvider));
});

final searchKnowledgeUseCaseProvider = Provider<SearchKnowledgeUseCase>((ref) {
  return SearchKnowledgeUseCase(ref.watch(knowledgeRepositoryProvider));
});

final manageWorkflowUseCaseProvider = Provider<ManageWorkflowUseCase>((ref) {
  return ManageWorkflowUseCase(ref.watch(automationRepositoryProvider));
});

final getNotificationsUseCaseProvider = Provider<GetNotificationsUseCase>((ref) {
  return GetNotificationsUseCase(ref.watch(notificationRepositoryProvider));
});

final executeQuickActionUseCaseProvider = Provider<ExecuteQuickActionUseCase>((ref) {
  return ExecuteQuickActionUseCase(ref.watch(quickActionRepositoryProvider));
});

final manageSessionsUseCaseProvider = Provider<ManageSessionsUseCase>((ref) {
  return ManageSessionsUseCase(ref.watch(securityRepositoryProvider));
});

final getSettingsUseCaseProvider = Provider<GetSettingsUseCase>((ref) {
  return GetSettingsUseCase(ref.watch(settingsRepositoryProvider));
});

final updateSettingsUseCaseProvider = Provider<UpdateSettingsUseCase>((ref) {
  return UpdateSettingsUseCase(ref.watch(settingsRepositoryProvider));
});

final getDiagnosticsUseCaseProvider = Provider<GetDiagnosticsUseCase>((ref) {
  return GetDiagnosticsUseCase(ref.watch(diagnosticsRepositoryProvider));
});

// ---------------------------------------------------------------------------
// Internal: bridge SendMessageUseCase via ConversationRepository
// ---------------------------------------------------------------------------
class _ConversationSendMessageUseCase implements SendMessageUseCase {
  final ConversationRepository _repo;
  _ConversationSendMessageUseCase(this._repo);

  @override
  Future<Result<Message>> call({
    required String conversationId,
    required String content,
    List<String>? attachmentIds,
  }) async {
    return _repo.sendMessage(
      conversationId: conversationId,
      content: content,
      attachmentIds: attachmentIds,
    );
  }
}
