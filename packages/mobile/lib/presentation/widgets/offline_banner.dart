import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/presentation/providers/connectivity_provider.dart';

class OfflineBanner extends ConsumerWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isConnected = ref.watch(connectivityProvider).valueOrNull ?? true;

    if (isConnected) return const SizedBox.shrink();

    return Semantics(
      liveRegion: true,
      label: 'You are offline',
      child: MaterialBanner(
        backgroundColor: AppTheme.warning.withValues(alpha: 0.15),
        content: Row(
          children: [
            Icon(
              Icons.wifi_off_rounded,
              size: AppSpacing.iconSm,
              color: AppTheme.warning,
            ),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: Text(
                'You are offline. Changes will sync when reconnected.',
                style: context.textTheme.bodySmall?.copyWith(
                  color: AppTheme.warning,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => ScaffoldMessenger.maybeOf(context)?.hideCurrentMaterialBanner(),
            child: const Text('Dismiss'),
          ),
        ],
      ),
    );
  }
}
