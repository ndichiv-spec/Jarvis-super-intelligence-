import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';

class SectionHeader extends StatelessWidget {
  const SectionHeader({
    super.key,
    required this.title,
    this.seeAllLabel,
    this.onSeeAll,
  });

  final String title;
  final String? seeAllLabel;
  final VoidCallback? onSeeAll;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: AppSpacing.horizontalMd.copyWith(top: AppSpacing.md, bottom: AppSpacing.sm),
      child: Semantics(
        header: true,
        child: Row(
          children: [
            Expanded(
              child: Text(
                title,
                style: context.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            if (onSeeAll != null)
              TextButton(
                onPressed: onSeeAll,
                child: Text(
                  seeAllLabel ?? 'See all',
                  style: context.textTheme.labelLarge?.copyWith(
                    color: context.colorScheme.primary,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
