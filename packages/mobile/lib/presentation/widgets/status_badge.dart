import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';

class StatusBadge extends StatelessWidget {
  const StatusBadge({
    super.key,
    required this.status,
    this.size = BadgeSize.small,
  });

  final String status;
  final BadgeSize size;

  Color _color() {
    final s = status.toLowerCase();
    if (s == 'running') return AppTheme.info;
    if (s == 'completed' || s == 'healthy') return AppTheme.success;
    if (s == 'failed' || s == 'error') return AppTheme.error;
    if (s == 'paused' || s == 'idle') return AppTheme.warning;
    return Colors.grey;
  }

  IconData? _icon() {
    final s = status.toLowerCase();
    if (s == 'running') return Icons.play_circle_filled;
    if (s == 'completed' || s == 'healthy') return Icons.check_circle;
    if (s == 'failed' || s == 'error') return Icons.cancel;
    if (s == 'paused') return Icons.pause_circle;
    if (s == 'idle') return Icons.hourglass_empty;
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final color = _color();
    final isSmall = size == BadgeSize.small;
    final icon = _icon();

    return Semantics(
      label: 'Status: $status',
      child: Container(
        padding: EdgeInsets.symmetric(
          horizontal: isSmall ? AppSpacing.sm : AppSpacing.md,
          vertical: isSmall ? 2.0 : AppSpacing.xs,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(AppSpacing.radiusXs),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(
                icon,
                size: isSmall ? AppSpacing.iconXs : AppSpacing.iconSm,
                color: color,
              ),
              const SizedBox(width: AppSpacing.xs),
            ],
            Text(
              status,
              style: TextStyle(
                fontSize: isSmall ? 11 : 12,
                fontWeight: FontWeight.w600,
                color: color,
                letterSpacing: 0.3,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

enum BadgeSize { small, medium }
