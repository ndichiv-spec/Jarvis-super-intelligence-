import 'package:flutter/material.dart';
import 'package:jarvis_mobile/presentation/providers/auth_provider.dart';
import 'package:jarvis_mobile/presentation/providers/automation_provider.dart';
import 'package:jarvis_mobile/presentation/providers/connectivity_provider.dart';
import 'package:jarvis_mobile/presentation/providers/conversation_provider.dart';
import 'package:jarvis_mobile/presentation/providers/diagnostics_provider.dart';
import 'package:jarvis_mobile/presentation/providers/knowledge_provider.dart';
import 'package:jarvis_mobile/presentation/providers/memory_provider.dart';
import 'package:jarvis_mobile/presentation/providers/notification_provider.dart';
import 'package:jarvis_mobile/presentation/providers/project_provider.dart';
import 'package:jarvis_mobile/presentation/providers/quick_action_provider.dart';
import 'package:jarvis_mobile/presentation/providers/security_provider.dart';
import 'package:jarvis_mobile/presentation/providers/settings_provider.dart';
import 'package:jarvis_mobile/presentation/providers/workspace_provider.dart';
import 'package:riverpod/riverpod.dart';

class AppState {
  final AuthState auth;
  final WorkspaceState workspace;
  final ConversationState conversation;
  final ProjectState project;
  final MemoryState memory;
  final KnowledgeState knowledge;
  final AutomationState automation;
  final NotificationState notification;
  final QuickActionState quickAction;
  final SecurityState security;
  final SettingsState settings;
  final DiagnosticsState diagnostics;
  final AsyncValue<bool> connectivity;
  final ThemeMode themeMode;

  const AppState({
    required this.auth,
    required this.workspace,
    required this.conversation,
    required this.project,
    required this.memory,
    required this.knowledge,
    required this.automation,
    required this.notification,
    required this.quickAction,
    required this.security,
    required this.settings,
    required this.diagnostics,
    required this.connectivity,
    required this.themeMode,
  });

  bool get isOffline => connectivity is AsyncData && (connectivity as AsyncData<bool>).value == false;

  bool get isAuthenticated => auth.isAuthenticated;

  bool get hasAnyLoading =>
      auth.isLoading ||
      workspace.isLoading ||
      conversation.isLoading ||
      project.isLoading ||
      memory.isLoading ||
      knowledge.isLoading ||
      automation.isLoading ||
      notification.isLoading ||
      quickAction.isLoading ||
      security.isLoading ||
      settings.isLoading ||
      diagnostics.isLoading;
}

final appStateProvider = Provider<AppState>((ref) {
  return AppState(
    auth: ref.watch(authProvider),
    workspace: ref.watch(workspaceProvider),
    conversation: ref.watch(conversationProvider),
    project: ref.watch(projectProvider),
    memory: ref.watch(memoryProvider),
    knowledge: ref.watch(knowledgeProvider),
    automation: ref.watch(automationProvider),
    notification: ref.watch(notificationProvider),
    quickAction: ref.watch(quickActionProvider),
    security: ref.watch(securityProvider),
    settings: ref.watch(settingsProvider),
    diagnostics: ref.watch(diagnosticsProvider),
    connectivity: ref.watch(connectivityProvider),
    themeMode: ref.watch(themeProvider),
  );
});
