import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/presentation/providers/security_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/empty_state.dart';
import 'package:jarvis_mobile/presentation/widgets/section_header.dart';

class SecurityPage extends ConsumerStatefulWidget {
  const SecurityPage({super.key});

  @override
  ConsumerState<SecurityPage> createState() => _SecurityPageState();
}

class _SecurityPageState extends ConsumerState<SecurityPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(securityProvider.notifier).loadAll();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(securityProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Security Center'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'Sessions (${state.sessions.length})'),
            Tab(text: 'Devices (${state.devices.length})'),
          ],
        ),
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _SessionsTab(sessions: state.sessions),
                _DevicesTab(devices: state.devices),
              ],
            ),
    );
  }
}

class _SessionsTab extends ConsumerWidget {
  final List<Session> sessions;

  const _SessionsTab({required this.sessions});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (sessions.isEmpty) {
      return const EmptyState(
        message: 'No active sessions',
        icon: Icons.lock_rounded,
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: sessions.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (_, i) {
        final session = sessions[i];
        final isExpired = session.expiresAt.isBefore(DateTime.now());

        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isExpired
                  ? AppTheme.error.withValues(alpha: 0.1)
                  : AppTheme.success.withValues(alpha: 0.1),
              child: Icon(
                isExpired ? Icons.lock_outline : Icons.lock_open_rounded,
                color: isExpired ? AppTheme.error : AppTheme.success,
              ),
            ),
            title: Text('Session ${session.id.substring(0, 8)}...'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  isExpired ? 'Expired' : 'Expires ${session.expiresAt.formatRelative()}',
                  style: TextStyle(color: isExpired ? AppTheme.error : null),
                ),
                if (session.workspaceId != null)
                  Text('Workspace: ${session.workspaceId}', style: context.textTheme.caption),
              ],
            ),
            trailing: Semantics(
              button: true,
              label: 'Revoke session',
              child: IconButton(
                icon: const Icon(Icons.logout, color: AppTheme.error),
                tooltip: 'Revoke',
                onPressed: () => ref.read(securityProvider.notifier).revokeSession(session.id),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _DevicesTab extends ConsumerWidget {
  final List<Device> devices;

  const _DevicesTab({required this.devices});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (devices.isEmpty) {
      return const EmptyState(
        message: 'No registered devices',
        icon: Icons.devices_rounded,
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: devices.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (_, i) {
        final device = devices[i];
        return Card(
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: device.isTrusted
                  ? AppTheme.success.withValues(alpha: 0.1)
                  : AppTheme.warning.withValues(alpha: 0.1),
              child: Icon(
                device.isTrusted ? Icons.trust_score : Icons.devices_other,
                color: device.isTrusted ? AppTheme.success : AppTheme.warning,
              ),
            ),
            title: Text(device.name),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('${device.type} \u2022 ${device.platform}'),
                Text('Last seen: ${device.lastSeenAt.formatRelative()}',
                    style: context.textTheme.caption),
              ],
            ),
            trailing: PopupMenuButton<String>(
              onSelected: (v) {
                if (v == 'trust') ref.read(securityProvider.notifier).trustDevice(device.id);
                if (v == 'remove') ref.read(securityProvider.notifier).removeDevice(device.id);
              },
              itemBuilder: (_) => [
                if (!device.isTrusted)
                  const PopupMenuItem(value: 'trust', child: Text('Trust Device')),
                if (!device.isCurrentDevice)
                  const PopupMenuItem(value: 'remove', child: Text('Remove Device')),
              ],
            ),
          ),
        );
      },
    );
  }
}
