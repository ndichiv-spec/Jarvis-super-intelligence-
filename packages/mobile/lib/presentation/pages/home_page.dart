import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/presentation/pages/ai_workspace_page.dart';
import 'package:jarvis_mobile/presentation/pages/automation_page.dart';
import 'package:jarvis_mobile/presentation/pages/diagnostics_page.dart';
import 'package:jarvis_mobile/presentation/pages/knowledge_page.dart';
import 'package:jarvis_mobile/presentation/pages/memory_page.dart';
import 'package:jarvis_mobile/presentation/pages/notification_page.dart';
import 'package:jarvis_mobile/presentation/pages/project_workspace_page.dart';
import 'package:jarvis_mobile/presentation/pages/security_page.dart';
import 'package:jarvis_mobile/presentation/pages/settings_page.dart';
import 'package:jarvis_mobile/presentation/providers/app_state_provider.dart';
import 'package:jarvis_mobile/presentation/providers/auth_provider.dart';
import 'package:jarvis_mobile/presentation/providers/automation_provider.dart';
import 'package:jarvis_mobile/presentation/providers/conversation_provider.dart';
import 'package:jarvis_mobile/presentation/providers/notification_provider.dart';
import 'package:jarvis_mobile/presentation/providers/project_provider.dart';
import 'package:jarvis_mobile/presentation/providers/quick_action_provider.dart';
import 'package:jarvis_mobile/presentation/providers/workspace_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/offline_banner.dart';
import 'package:jarvis_mobile/presentation/widgets/quick_action_chip.dart';
import 'package:jarvis_mobile/presentation/widgets/section_header.dart';

enum _AppTab { home, workspace, notifications, account }

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  _AppTab _currentTab = _AppTab.home;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
          ref.read(workspaceProvider.notifier).loadWorkspaces();
      ref.read(conversationProvider.notifier).list('');
      ref.read(projectProvider.notifier).list('');
      ref.read(automationProvider.notifier).list();
      ref.read(notificationProvider.notifier).list();
      ref.read(quickActionProvider.notifier).list();
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final appState = ref.watch(appStateProvider);
    final quickActions = ref.watch(quickActionProvider);

    return Scaffold(
      body: Column(
        children: [
          const OfflineBanner(),
          Expanded(child: _buildBody(auth, appState, quickActions)),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _AppTab.values.indexOf(_currentTab),
        onDestinationSelected: (i) => setState(() => _currentTab = _AppTab.values[i]),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.workspace_premium_outlined), selectedIcon: Icon(Icons.workspace_premium), label: 'Workspace'),
          NavigationDestination(icon: Icon(Icons.notifications_outlined), selectedIcon: Icon(Icons.notifications), label: 'Activity'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Account'),
        ],
      ),
    );
  }

  Widget _buildBody(AuthState auth, AppState appState, QuickActionState quickActions) {
    switch (_currentTab) {
      case _AppTab.home:
        return _HomeTab(
          auth: auth,
          appState: appState,
          quickActions: quickActions.actions,
          onQuickAction: (id) => ref.read(quickActionProvider.notifier).execute(id),
        );
      case _AppTab.workspace:
        return const ProjectWorkspacePage();
      case _AppTab.notifications:
        return const NotificationPage();
      case _AppTab.account:
        return _AccountTab();
    }
  }
}

class _HomeTab extends ConsumerWidget {
  const _HomeTab({
    required this.auth,
    required this.appState,
    required this.quickActions,
    required this.onQuickAction,
  });

  final AuthState auth;
  final AppState appState;
  final List<QuickAction> quickActions;
  final void Function(String id) onQuickAction;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final safeQuickActions = quickActions.where((a) => a.isEnabled).take(6).toList();

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
      ref.read(workspaceProvider.notifier).loadWorkspaces();
          ref.read(conversationProvider.notifier).list('');
          ref.read(projectProvider.notifier).list('');
          ref.read(automationProvider.notifier).list();
          ref.read(notificationProvider.notifier).list();
          ref.read(quickActionProvider.notifier).list();
        },
        child: ListView(
          padding: AppSpacing.paddingMd,
          children: [
            Semantics(
              header: true,
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: context.colorScheme.primaryContainer,
                    child: Icon(Icons.psychology, color: context.colorScheme.onPrimaryContainer),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Welcome,', style: context.textTheme.bodySmall),
                      Text(
                        auth.user?.displayName ?? 'Explorer',
                        style: context.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
                      ),
                    ],
                  ),
                  const Spacer(),
                  Semantics(
                    button: true,
                    label: 'Notifications',
                    child: Badge(
                      isLabelVisible: appState.notification.unreadCount > 0,
                      label: Text('${appState.notification.unreadCount}'),
                      child: IconButton(
                        icon: const Icon(Icons.notifications_outlined),
                        onPressed: () {},
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            if (safeQuickActions.isNotEmpty) ...[
              SizedBox(
                height: 40,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: safeQuickActions.length,
                  separatorBuilder: (_, __) => const SizedBox(width: AppSpacing.sm),
                  itemBuilder: (_, i) {
                    final action = safeQuickActions[i];
                    return QuickActionChip(
                      label: action.label,
                      icon: Icons.flash_on,
                      onTap: () => onQuickAction(action.id),
                    );
                  },
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
            ],
            _MetricsGrid(appState: appState),
            const SizedBox(height: AppSpacing.md),
            SectionHeader(
              title: 'Conversations',
              onSeeAll: () => ref.read(conversationProvider.notifier).list(''),
            ),
            if (appState.conversation.conversations.isEmpty)
              _EmptyHint('Start a conversation to begin')
            else
              ...appState.conversation.conversations.take(3).map(
                (c) => ListTile(
                  leading: CircleAvatar(
                    backgroundColor: context.colorScheme.primaryContainer,
                    child: Icon(Icons.chat, size: 18, color: context.colorScheme.onPrimaryContainer),
                  ),
                  title: Text(c.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                  subtitle: Text('${c.messageCount} messages', style: context.textTheme.bodySmall),
                  onTap: () {},
                ),
              ),
            if (appState.project.projects.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.md),
              SectionHeader(title: 'Active Projects'),
              ...appState.project.projects.take(3).map(
                (p) => ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppTheme.primary.withValues(alpha: 0.1),
                    child: Text(
                      p.name.isNotEmpty ? p.name[0].toUpperCase() : '?',
                      style: const TextStyle(fontWeight: FontWeight.w700, color: AppTheme.primary),
                    ),
                  ),
                  title: Text(p.name, maxLines: 1, overflow: TextOverflow.ellipsis),
                  subtitle: LinearProgressIndicator(value: p.progress.clamp(0, 1)),
                  onTap: () {},
                ),
              ),
            ],
            if (appState.automation.workflows.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.md),
              SectionHeader(title: 'Running Automations'),
              ...appState.automation.workflows
                  .where((w) => w.status == WorkflowStatus.running)
                  .take(3).map(
                (w) => ListTile(
                  leading: const Icon(Icons.play_circle, color: AppTheme.success),
                  title: Text(w.name, maxLines: 1, overflow: TextOverflow.ellipsis),
                  subtitle: Text(w.status.name, style: context.textTheme.bodySmall),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MetricsGrid extends StatelessWidget {
  final AppState appState;

  const _MetricsGrid({required this.appState});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Platform metrics',
      child: Wrap(
        spacing: AppSpacing.sm,
        runSpacing: AppSpacing.sm,
        children: [
          _MetricTile(
            icon: Icons.chat_rounded,
            label: 'Conversations',
            value: '${appState.conversation.conversations.length}',
            color: context.colorScheme.primary,
          ),
          _MetricTile(
            icon: Icons.folder_rounded,
            label: 'Projects',
            value: '${appState.project.projects.length}',
            color: context.colorScheme.secondary,
          ),
          _MetricTile(
            icon: Icons.psychology_rounded,
            label: 'Memories',
            value: '${appState.memory.items.length}',
            color: context.colorScheme.tertiary,
          ),
          _MetricTile(
            icon: Icons.rocket_launch_rounded,
            label: 'Workflows',
            value: '${appState.automation.workflows.length}',
            color: AppTheme.success,
          ),
        ],
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _MetricTile({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: '$label: $value',
      child: SizedBox(
        width: (MediaQuery.of(context).size.width - AppSpacing.md * 2 - AppSpacing.sm * 3) / 4,
        child: Card(
          child: Padding(
            padding: AppSpacing.paddingSm,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 20, color: color),
                const SizedBox(height: 4),
                Text(value, style: context.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
                Text(label, style: context.textTheme.caption, maxLines: 1, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EmptyHint extends StatelessWidget {
  final String message;

  const _EmptyHint(this.message);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Text(message,
        style: context.textTheme.bodyMedium?.copyWith(color: context.colorScheme.onSurfaceVariant),
        textAlign: TextAlign.center,
      ),
    );
  }
}

class _AccountTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);

    return SafeArea(
      child: ListView(
        padding: AppSpacing.paddingMd,
        children: [
          Semantics(
            header: true,
            child: Center(
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 40,
                    backgroundColor: context.colorScheme.primaryContainer,
                    child: Icon(Icons.person, size: 40, color: context.colorScheme.onPrimaryContainer),
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  Text(auth.user?.displayName ?? 'User', style: context.textTheme.titleLarge),
                  if (auth.user?.email != null)
                    Text(auth.user!.email!, style: context.textTheme.bodySmall),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          _AccountTile(
            icon: Icons.psychology_rounded,
            title: 'AI Workspace',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AiWorkspacePage())),
          ),
          _AccountTile(
            icon: Icons.memory_rounded,
            title: 'Memory Center',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const MemoryPage())),
          ),
          _AccountTile(
            icon: Icons.explore_rounded,
            title: 'Knowledge Explorer',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const KnowledgePage())),
          ),
          _AccountTile(
            icon: Icons.rocket_launch_rounded,
            title: 'Automation Center',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AutomationPage())),
          ),
          _AccountTile(
            icon: Icons.shield_rounded,
            title: 'Security Center',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SecurityPage())),
          ),
          _AccountTile(
            icon: Icons.settings_rounded,
            title: 'Settings',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsPage())),
          ),
          _AccountTile(
            icon: Icons.diagnostics_rounded,
            title: 'Diagnostics',
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const DiagnosticsPage())),
          ),
          const Divider(height: AppSpacing.xl),
          Semantics(
            button: true,
            label: 'Sign out',
            child: ListTile(
              leading: const Icon(Icons.logout, color: AppTheme.error),
              title: const Text('Sign Out', style: TextStyle(color: AppTheme.error)),
              onTap: () => ref.read(authProvider.notifier).logout(),
            ),
          ),
        ],
      ),
    );
  }
}

class _AccountTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _AccountTile({required this.icon, required this.title, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: title,
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
