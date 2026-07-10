import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';

class QuickActionChip extends StatelessWidget {
  const QuickActionChip({
    super.key,
    required this.label,
    required this.icon,
    this.onTap,
    this.isEnabled = true,
  });

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final bool isEnabled;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: isEnabled,
      label: label,
      child: ActionChip(
        onPressed: isEnabled ? onTap : null,
        avatar: Icon(
          icon,
          size: AppSpacing.iconSm,
          color: isEnabled
              ? context.colorScheme.primary
              : context.colorScheme.onSurface.withValues(alpha: 0.38),
        ),
        label: Text(
          label,
          style: context.textTheme.labelMedium?.copyWith(
            color: isEnabled ? null : context.colorScheme.onSurface.withValues(alpha: 0.38),
          ),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
          side: BorderSide(
            color: isEnabled
                ? context.colorScheme.outline.withValues(alpha: 0.5)
                : context.colorScheme.outline.withValues(alpha: 0.2),
          ),
        ),
      ),
    );
  }
}
