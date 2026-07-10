import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/presentation/widgets/section_header.dart';

class SectionList<T> extends StatelessWidget {
  const SectionList({
    super.key,
    required this.sections,
    this.itemBuilder,
    this.headerBuilder,
    this.emptyMessage = 'No items',
    this.emptyIcon,
    this.physics,
    this.padding,
  });

  final List<Section<T>> sections;
  final Widget Function(BuildContext, T, int)? itemBuilder;
  final Widget Function(BuildContext, String)? headerBuilder;
  final String emptyMessage;
  final IconData? emptyIcon;
  final ScrollPhysics? physics;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final hasItems = sections.any((s) => s.items.isNotEmpty);

    if (!hasItems) {
      return Center(
        child: Padding(
          padding: AppSpacing.paddingXl,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                emptyIcon ?? Icons.inbox_rounded,
                size: AppSpacing.iconXl,
                color: context.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
              ),
              const SizedBox(height: AppSpacing.md),
              Text(
                emptyMessage,
                style: context.textTheme.bodyLarge?.copyWith(
                  color: context.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      physics: physics,
      padding: padding ?? AppSpacing.verticalSm,
      itemCount: sections.length,
      itemBuilder: (context, index) {
        final section = sections[index];
        if (section.items.isEmpty) return const SizedBox.shrink();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (headerBuilder != null)
              headerBuilder!(context, section.title)
            else
              SectionHeader(title: section.title),
            ...List.generate(section.items.length, (i) {
              return itemBuilder?.call(context, section.items[i], i) ?? const SizedBox.shrink();
            }),
          ],
        );
      },
    );
  }
}

class Section<T> {
  final String title;
  final List<T> items;

  const Section({
    required this.title,
    required this.items,
  });
}
