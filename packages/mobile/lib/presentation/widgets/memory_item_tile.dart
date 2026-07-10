import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/domain/entities/memory_item.dart';

class MemoryItemTile extends StatelessWidget {
  const MemoryItemTile({
    super.key,
    required this.memoryItem,
    this.onTap,
    this.onArchive,
    this.onDelete,
  });

  final MemoryItem memoryItem;
  final VoidCallback? onTap;
  final VoidCallback? onArchive;
  final VoidCallback? onDelete;

  Color _importanceColor(int importance, ColorScheme scheme) {
    if (importance >= 8) return scheme.error;
    if (importance >= 5) return scheme.tertiary;
    if (importance >= 3) return scheme.secondary;
    return scheme.outline;
  }

  IconData _typeIcon(String type) {
    switch (type.toLowerCase()) {
      case 'note':
        return Icons.note_rounded;
      case 'fact':
        return Icons.psychology_rounded;
      case 'preference':
        return Icons.favorite_rounded;
      case 'event':
        return Icons.event_rounded;
      case 'reminder':
        return Icons.notifications_rounded;
      case 'task':
        return Icons.task_alt_rounded;
      default:
        return Icons.memory_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = context.colorScheme;
    final impColor = _importanceColor(memoryItem.importance, scheme);

    return Semantics(
      button: true,
      label: 'Memory: ${memoryItem.content}',
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: impColor.withValues(alpha: 0.12),
          radius: 20,
          child: Icon(
            _typeIcon(memoryItem.type),
            size: AppSpacing.iconSm,
            color: impColor,
          ),
        ),
        title: Text(
          memoryItem.content,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: context.textTheme.bodyMedium,
        ),
        subtitle: Row(
          children: [
            Icon(Icons.source_rounded, size: 12, color: scheme.onSurfaceVariant),
            const SizedBox(width: AppSpacing.xs),
            Text(
              memoryItem.source,
              style: context.textTheme.bodySmall?.copyWith(
                color: scheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!memoryItem.isArchived && onArchive != null)
              IconButton(
                icon: const Icon(Icons.archive_outline_rounded),
                iconSize: AppSpacing.iconSm,
                onPressed: onArchive,
                tooltip: 'Archive',
              ),
            if (onDelete != null)
              IconButton(
                icon: const Icon(Icons.delete_outline_rounded),
                iconSize: AppSpacing.iconSm,
                onPressed: onDelete,
                tooltip: 'Delete',
              ),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
}
