import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';

class SearchBarWidget extends StatelessWidget {
  const SearchBarWidget({
    super.key,
    this.hint = 'Search...',
    this.onChanged,
    this.onSubmitted,
    this.onFilter,
    this.controller,
    this.autofocus = false,
  });

  final String hint;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onFilter;
  final TextEditingController? controller;
  final bool autofocus;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Search',
      child: Padding(
        padding: AppSpacing.horizontalMd.copyWith(
          top: AppSpacing.sm,
          bottom: AppSpacing.sm,
        ),
        child: TextField(
          controller: controller,
          autofocus: autofocus,
          onChanged: onChanged,
          onSubmitted: onSubmitted,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: const Icon(Icons.search_rounded),
            suffixIcon: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (onFilter != null)
                  IconButton(
                    icon: const Icon(Icons.tune_rounded),
                    onPressed: onFilter,
                    tooltip: 'Filters',
                  ),
                if (controller != null && controller!.text.isNotEmpty)
                  IconButton(
                    icon: const Icon(Icons.clear_rounded),
                    onPressed: () {
                      controller!.clear();
                      onChanged?.call('');
                    },
                    tooltip: 'Clear',
                  ),
              ],
            ),
            filled: true,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.md,
              vertical: 12,
            ),
          ),
        ),
      ),
    );
  }
}
