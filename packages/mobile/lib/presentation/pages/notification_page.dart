import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart';
import 'package:jarvis_mobile/presentation/providers/notification_provider.dart';

enum _NotificationGroup { today, yesterday, older }

class NotificationPage extends ConsumerStatefulWidget {
  const NotificationPage({super.key});

  @override
  ConsumerState<NotificationPage> createState() => _NotificationPageState();
}

class _NotificationPageState extends ConsumerState<NotificationPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(notificationProvider.notifier).list();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(notificationProvider);
    final grouped = _groupNotifications(state.notifications);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          if (state.unreadCount > 0)
            Semantics(
              label: 'Mark all notifications as read',
              button: true,
              child: IconButton(
                icon: const Icon(Icons.done_all),
                tooltip: 'Mark all read',
                onPressed: () => ref.read(notificationProvider.notifier).markAllRead(),
              ),
            ),
        ],
      ),
      body: _buildBody(context, state, grouped),
    );
  }

  Widget _buildBody(
    BuildContext context,
    NotificationState state,
    Map<_NotificationGroup, List<Notification>> grouped,
  ) {
    if (state.isLoading && state.notifications.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.notifications.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.notifications_none, size: 48, color: Colors.grey),
            SizedBox(height: AppSpacing.md),
            Text('No notifications', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return ListView(
      padding: AppSpacing.paddingMd,
      children: [
        for (final group in _NotificationGroup.values)
          if (grouped.containsKey(group)) ...[
            _SectionHeader(
              label: switch (group) {
                _NotificationGroup.today => 'Today',
                _NotificationGroup.yesterday => 'Yesterday',
                _NotificationGroup.older => 'Older',
              },
            ),
            ...grouped[group]!.map((n) => _NotificationTile(notification: n)),
          ],
      ],
    );
  }

  Map<_NotificationGroup, List<Notification>> _groupNotifications(
    List<Notification> notifications,
  ) {
    final grouped = <_NotificationGroup, List<Notification>>{};
    for (final n in notifications) {
      final g = switch (n.createdAt) {
        final d when d.isToday => _NotificationGroup.today,
        final d when d.isYesterday => _NotificationGroup.yesterday,
        _ => _NotificationGroup.older,
      };
      grouped.putIfAbsent(g, () => []).add(n);
    }
    return grouped;
  }
}

class _SectionHeader extends StatelessWidget {
  final String label;

  const _SectionHeader({required this.label});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      header: true,
      child: Padding(
        padding: const EdgeInsets.only(
          top: AppSpacing.md,
          bottom: AppSpacing.sm,
        ),
        child: Text(
          label,
          style: context.textTheme.titleSmall?.copyWith(
            color: context.colorScheme.primary,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}

class _NotificationTile extends ConsumerWidget {
  final Notification notification;

  const _NotificationTile({required this.notification});

  IconData _iconForType(String type) {
    return switch (type) {
      'alert' => Icons.warning_amber_rounded,
      'info' => Icons.info_outline,
      'success' => Icons.check_circle_outline,
      'error' => Icons.error_outline,
      'sync' => Icons.sync,
      'message' => Icons.message_outlined,
      _ => Icons.notifications_outlined,
    };
  }

  Color _colorForType(String type) {
    return switch (type) {
      'alert' => AppTheme.warning,
      'info' => AppTheme.info,
      'success' => AppTheme.success,
      'error' => AppTheme.error,
      'sync' => AppTheme.primary,
      'message' => AppTheme.accent,
      _ => Colors.grey,
    };
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Semantics(
      button: true,
      label: '${notification.title}. ${notification.body}',
      child: Dismissible(
        key: ValueKey(notification.id),
        direction: DismissDirection.endToStart,
        background: Container(
          alignment: Alignment.centerRight,
          padding: AppSpacing.horizontalMd,
          color: AppTheme.primary,
          child: const Icon(Icons.check, color: Colors.white),
        ),
        onDismissed: (_) {
          ref.read(notificationProvider.notifier).markRead(notification.id);
        },
        child: Card(
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.md,
              vertical: AppSpacing.sm,
            ),
            leading: Semantics(
              container: true,
              child: Icon(
                _iconForType(notification.type),
                color: _colorForType(notification.type),
              ),
            ),
            title: Row(
              children: [
                if (!notification.isRead)
                  Semantics(
                    label: 'Unread',
                    container: true,
                    child: Container(
                      width: 8,
                      height: 8,
                      margin: const EdgeInsets.only(right: AppSpacing.sm),
                      decoration: const BoxDecoration(
                        color: AppTheme.primary,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                Expanded(
                  child: Text(
                    notification.title,
                    style: context.textTheme.titleSmall?.copyWith(
                      fontWeight: notification.isRead ? FontWeight.w400 : FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(notification.body, style: context.textTheme.bodySmall),
                const SizedBox(height: 2),
                Text(
                  notification.createdAt.formatRelative(),
                  style: context.textTheme.caption?.copyWith(color: Colors.grey),
                ),
              ],
            ),
            onTap: () {
              if (!notification.isRead) {
                ref.read(notificationProvider.notifier).markRead(notification.id);
              }
            },
          ),
        ),
      ),
    );
  }
}
