import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/presentation/providers/knowledge_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/empty_state.dart';
import 'package:jarvis_mobile/presentation/widgets/search_bar_widget.dart';

class KnowledgePage extends ConsumerStatefulWidget {
  const KnowledgePage({super.key});

  @override
  ConsumerState<KnowledgePage> createState() => _KnowledgePageState();
}

class _KnowledgePageState extends ConsumerState<KnowledgePage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(knowledgeProvider.notifier).listCollections();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(knowledgeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Knowledge Explorer'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Collections'),
            Tab(text: 'Search'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _CollectionsTab(state: state),
          _SearchTab(state: state, searchController: _searchController),
        ],
      ),
    );
  }
}

class _CollectionsTab extends ConsumerWidget {
  final KnowledgeState state;

  const _CollectionsTab({required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (state.isLoading && state.collections.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.collections.isEmpty) {
      return const EmptyState(
        message: 'No knowledge collections',
        icon: Icons.menu_book_rounded,
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: state.collections.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (_, i) {
        final collection = state.collections[i];
        return Semantics(
          button: true,
          label: 'Collection: ${collection.name}',
          child: Card(
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: context.colorScheme.primaryContainer,
                child: Icon(Icons.collections_bookmark_rounded, color: context.colorScheme.onPrimaryContainer),
              ),
              title: Text(collection.name, style: context.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
              subtitle: Text('${collection.documentCount} documents'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => ref.read(knowledgeProvider.notifier).selectCollection(collection.id),
            ),
          ),
        );
      },
    );
  }
}

class _SearchTab extends ConsumerStatefulWidget {
  final KnowledgeState state;
  final TextEditingController searchController;

  const _SearchTab({required this.state, required this.searchController});

  @override
  ConsumerState<_SearchTab> createState() => _SearchTabState();
}

class _SearchTabState extends ConsumerState<_SearchTab> {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SearchBarWidget(
          hint: 'Search knowledge...',
          controller: widget.searchController,
          onSubmitted: (q) {
            if (q.trim().isNotEmpty) {
              ref.read(knowledgeProvider.notifier).search(q);
            }
          },
        ),
        Expanded(
          child: widget.state.isLoading
              ? const Center(child: CircularProgressIndicator())
              : widget.state.searchResults.isEmpty
                  ? const EmptyState(
                      message: 'Search knowledge to find documents',
                      icon: Icons.search_rounded,
                    )
                  : ListView.separated(
                      padding: AppSpacing.horizontalMd,
                      itemCount: widget.state.searchResults.length,
                      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
                      itemBuilder: (_, i) {
                        final doc = widget.state.searchResults[i];
                        return Semantics(
                          button: true,
                          label: 'Document: ${doc.title}',
                          child: Card(
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: context.colorScheme.secondaryContainer,
                                child: Icon(Icons.article_rounded, color: context.colorScheme.onSecondaryContainer),
                              ),
                              title: Text(doc.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                              subtitle: Row(
                                children: [
                                  Text(doc.documentType.toUpperCase(), style: context.textTheme.caption),
                                  const SizedBox(width: AppSpacing.sm),
                                  Text(doc.createdAt.formatShort(), style: context.textTheme.caption),
                                ],
                              ),
                              trailing: const Icon(Icons.open_in_new_rounded, size: 18),
                              onTap: () {},
                            ),
                          ),
                        );
                      },
                    ),
        ),
      ],
    );
  }
}
