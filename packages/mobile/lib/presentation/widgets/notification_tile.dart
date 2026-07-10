import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart';

class NotificationTile extends StatelessWidget {
  const NotificationTile({
    super.key,
    required this.notification,
    this.onTap,
  });

  final Notification notification;
  final VoidCallback? onTap;

  IconData _iconForType(String type) {
    switch (type.toLowerCase()) {
      case 'message':
        return Icons.chat_rounded;
      case 'alert':
      case 'warning':
        return Icons.warning_amber_rounded;
      case 'error':
        return Icons.error_outline_rounded;
      case 'success':
        return Icons.check_circle_outline_rounded;
      case 'update':
        return Icons.system_update_rounded;
      case 'mention':
        return Icons.alternate_email_rounded;
      case 'reminder':
        return Icons.notifications_active_rounded;
      default:
        return Icons.notifications_outlined;
    }
  }

  Color _colorForType(String type, ColorScheme scheme) {
    switch (type.toLowerCase()) {
      case 'message':
      case 'mention':
        return scheme.primary;
      case 'warning':
        return scheme.errorContainer;
      case 'error':
        return scheme.error;
      case 'success':
        return scheme.tertiary;
      case 'update':
        return scheme.secondary;
      default:
        return scheme.onSurfaceVariant;
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = context.colorScheme;
    final iconColor = _colorForType(notification.type, scheme);

    return Semantics(
      button: true,
      label: '${notification.title}. ${notification.body}',
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: iconColor.withValues(alpha: 0.12),
          radius: 20,
          child: Icon(
            _iconForType(notification.type),
            size: AppSpacing.iconSm,
            color: iconColor,
          ),
        ),
        title: Text(
          notification.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: context.textTheme.bodyMedium?.copyWith(
            fontWeight: notification.isRead ? FontWeight.normal : FontWeight.w600,
          ),
        ),
        subtitle: Text(
          notification.body,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: context.textTheme.bodySmall?.copyWith(
            color: context.colorScheme.onSurfaceVariant,
          ),
        ),
        trailing: Text(
          notification.createdAt.formatRelative(),
          style: context.textTheme.labelSmall?.copyWith(
            color: context.colorScheme.onSurfaceVariant,
          ),
        ),
        onTap: onTap,
      ),
    );
  }
}
