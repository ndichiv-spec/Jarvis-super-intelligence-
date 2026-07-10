import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/presentation/providers/project_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/empty_state.dart';
import 'package:jarvis_mobile/presentation/widgets/section_header.dart';

class ProjectWorkspacePage extends ConsumerStatefulWidget {
  const ProjectWorkspacePage({super.key});

  @override
  ConsumerState<ProjectWorkspacePage> createState() => _ProjectWorkspacePageState();
}

class _ProjectWorkspacePageState extends ConsumerState<ProjectWorkspacePage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(projectProvider.notifier).list('');
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(projectProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Project Workspace'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'All Projects'),
            Tab(text: 'Active'),
            Tab(text: 'Completed'),
          ],
        ),
      ),
      body: state.isLoading && state.projects.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : state.projects.isEmpty
              ? const EmptyState(
                  message: 'No projects yet',
                  icon: Icons.folder_open_rounded,
                )
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _ProjectList(projects: state.projects),
                    _ProjectList(projects: state.projects.where((p) => p.status == 'active').toList()),
                    _ProjectList(projects: state.projects.where((p) => p.status == 'completed').toList()),
                  ],
                ),
    );
  }
}

class _ProjectList extends ConsumerWidget {
  final List<Project> projects;

  const _ProjectList({required this.projects});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (projects.isEmpty) {
      return const EmptyState(
        message: 'No projects in this category',
        icon: Icons.folder_off_rounded,
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: projects.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (_, i) {
        final project = projects[i];
        return Semantics(
          button: true,
          label: 'Project: ${project.name}',
          child: Card(
            child: ExpansionTile(
              leading: CircleAvatar(
                backgroundColor: context.colorScheme.primaryContainer,
                child: Text(
                  project.name.isNotEmpty ? project.name[0].toUpperCase() : '?',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: context.colorScheme.onPrimaryContainer,
                  ),
                ),
              ),
              title: Text(project.name, style: context.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (project.description != null && project.description!.isNotEmpty)
                    Text(project.description!, maxLines: 2, overflow: TextOverflow.ellipsis),
                  const SizedBox(height: AppSpacing.xs),
                  LinearProgressIndicator(value: project.progress.clamp(0, 1)),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    'Updated ${project.updatedAt.formatRelative()}',
                    style: context.textTheme.caption?.copyWith(color: context.colorScheme.onSurfaceVariant),
                  ),
                ],
              ),
              children: [
                ListTile(
                  leading: const Icon(Icons.chat_rounded),
                  title: const Text('Conversations'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {},
                ),
                ListTile(
                  leading: const Icon(Icons.rocket_launch_rounded),
                  title: const Text('Workflows'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {},
                ),
                ListTile(
                  leading: const Icon(Icons.menu_book_rounded),
                  title: const Text('Knowledge'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {},
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
