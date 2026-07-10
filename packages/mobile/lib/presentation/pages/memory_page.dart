import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/presentation/providers/memory_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/empty_state.dart';
import 'package:jarvis_mobile/presentation/widgets/search_bar_widget.dart';

class MemoryPage extends ConsumerStatefulWidget {
  const MemoryPage({super.key});

  @override
  ConsumerState<MemoryPage> createState() => _MemoryPageState();
}

class _MemoryPageState extends ConsumerState<MemoryPage> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(memoryProvider.notifier).list();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(memoryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Memory Center'),
      ),
      body: Column(
        children: [
          SearchBarWidget(
            hint: 'Search memories...',
            controller: _searchController,
            onChanged: (q) {
              if (q.length > 2) {
                ref.read(memoryProvider.notifier).search(q);
              } else if (q.isEmpty) {
                ref.read(memoryProvider.notifier).list();
              }
            },
          ),
          Expanded(
            child: state.isLoading
                ? const Center(child: CircularProgressIndicator())
                : state.items.isEmpty
                    ? const EmptyState(
                        message: 'No memories found',
                        icon: Icons.memory_rounded,
                      )
                    : ListView.builder(
                        padding: AppSpacing.horizontalMd,
                        itemCount: state.items.length,
                        itemBuilder: (_, i) {
                          final item = state.items[i];
                          return _MemoryCard(
                            item: item,
                            onArchive: () => ref.read(memoryProvider.notifier).archive(item.id),
                            onDelete: () => ref.read(memoryProvider.notifier).delete(item.id),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}

class _MemoryCard extends StatelessWidget {
  final MemoryItem item;
  final VoidCallback onArchive;
  final VoidCallback onDelete;

  const _MemoryCard({
    required this.item,
    required this.onArchive,
    required this.onDelete,
  });

  Color _importanceColor(int importance, ColorScheme scheme) {
    if (importance >= 8) return scheme.error;
    if (importance >= 5) return scheme.tertiary;
    if (importance >= 3) return scheme.secondary;
    return scheme.outline;
  }

  IconData _typeIcon(String type) {
    switch (type.toLowerCase()) {
      case 'note': return Icons.note_rounded;
      case 'fact': return Icons.psychology_rounded;
      case 'preference': return Icons.favorite_rounded;
      case 'event': return Icons.event_rounded;
      case 'reminder': return Icons.notifications_rounded;
      case 'task': return Icons.task_alt_rounded;
      default: return Icons.memory_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = context.colorScheme;
    final color = _importanceColor(item.importance, scheme);

    return Card(
      margin: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withValues(alpha: 0.12),
          child: Icon(_typeIcon(item.type), color: color),
        ),
        title: Text(item.content, maxLines: 2, overflow: TextOverflow.ellipsis),
        subtitle: Row(
          children: [
            Icon(Icons.source_rounded, size: 12, color: scheme.onSurfaceVariant),
            const SizedBox(width: AppSpacing.xs),
            Text(item.source, style: context.textTheme.caption),
            const Spacer(),
            Text('${item.importance}', style: TextStyle(color: color, fontWeight: FontWeight.w600)),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (v) {
            if (v == 'archive') onArchive();
            if (v == 'delete') onDelete();
          },
          itemBuilder: (_) => [
            const PopupMenuItem(value: 'archive', child: Text('Archive')),
            const PopupMenuItem(value: 'delete', child: Text('Delete')),
          ],
        ),
      ),
    );
  }
}
