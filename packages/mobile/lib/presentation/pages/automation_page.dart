import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/entities/workflow_execution.dart';
import 'package:jarvis_mobile/presentation/providers/automation_provider.dart';

class AutomationPage extends ConsumerStatefulWidget {
  const AutomationPage({super.key});

  @override
  ConsumerState<AutomationPage> createState() => _AutomationPageState();
}

class _AutomationPageState extends ConsumerState<AutomationPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(automationProvider.notifier).list();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(automationProvider);
    final running = state.workflows.where((w) => w.status == WorkflowStatus.running).toList();
    final scheduled = state.workflows.where((w) => w.status == WorkflowStatus.idle || w.status == WorkflowStatus.paused).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Automation'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Running'),
            Tab(text: 'Scheduled'),
            Tab(text: 'History'),
          ],
        ),
      ),
      body: state.isLoading && state.workflows.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _RunningTab(workflows: running),
                _ScheduledTab(workflows: scheduled),
                _HistoryTab(history: state.history),
              ],
            ),
    );
  }
}

class _RunningTab extends ConsumerWidget {
  final List<Workflow> workflows;

  const _RunningTab({required this.workflows});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (workflows.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.check_circle_outline, size: 48, color: Colors.grey),
            SizedBox(height: AppSpacing.md),
            Text('No running workflows', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: workflows.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final w = workflows[index];
        return Semantics(
          button: true,
          child: Card(
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.sm,
              ),
              leading: Semantics(
                container: true,
                child: const Icon(Icons.play_circle_filled, color: AppTheme.success),
              ),
              title: Semantics(
                header: true,
                child: Text(w.name, style: context.textTheme.titleMedium),
              ),
              subtitle: w.description != null ? Text(w.description!) : null,
              trailing: Semantics(
                container: true,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Semantics(
                      label: 'Pause ${w.name}',
                      button: true,
                      child: IconButton(
                        icon: const Icon(Icons.pause_circle_filled, color: AppTheme.warning),
                        tooltip: 'Pause',
                        onPressed: () => ref.read(automationProvider.notifier).pause(w.id),
                      ),
                    ),
                    Semantics(
                      label: 'Cancel ${w.name}',
                      button: true,
                      child: IconButton(
                        icon: const Icon(Icons.cancel, color: AppTheme.error),
                        tooltip: 'Cancel',
                        onPressed: () => ref.read(automationProvider.notifier).cancelExecution(w.id),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _ScheduledTab extends ConsumerWidget {
  final List<Workflow> workflows;

  const _ScheduledTab({required this.workflows});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (workflows.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.schedule, size: 48, color: Colors.grey),
            SizedBox(height: AppSpacing.md),
            Text('No scheduled workflows', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: workflows.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final w = workflows[index];
        final isPaused = w.status == WorkflowStatus.paused;

        return Semantics(
          button: true,
          child: Card(
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.sm,
              ),
              leading: Semantics(
                container: true,
                child: Icon(
                  isPaused ? Icons.pause_circle_filled : Icons.schedule,
                  color: isPaused ? AppTheme.warning : AppTheme.primary,
                ),
              ),
              title: Semantics(
                header: true,
                child: Text(w.name, style: context.textTheme.titleMedium),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (w.description != null) Text(w.description!),
                  if (w.nextRunAt != null)
                    Text(
                      'Next: ${w.nextRunAt!.formatRelative()}',
                      style: context.textTheme.bodySmall?.copyWith(color: Colors.grey),
                    ),
                  if (w.trigger != null)
                    Text(
                      'Trigger: ${w.trigger}',
                      style: context.textTheme.bodySmall?.copyWith(color: Colors.grey),
                    ),
                ],
              ),
              trailing: Semantics(
                label: isPaused ? 'Resume ${w.name}' : 'Pause ${w.name}',
                button: true,
                child: IconButton(
                  icon: Icon(
                    isPaused ? Icons.play_arrow : Icons.pause,
                  ),
                  tooltip: isPaused ? 'Resume' : 'Pause',
                  onPressed: () {
                    final notifier = ref.read(automationProvider.notifier);
                    if (isPaused) {
                      notifier.resume(w.id);
                    } else {
                      notifier.pause(w.id);
                    }
                  },
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _HistoryTab extends ConsumerWidget {
  final List<WorkflowExecution> history;

  const _HistoryTab({required this.history});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (history.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.history, size: 48, color: Colors.grey),
            SizedBox(height: AppSpacing.md),
            Text('No execution history', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: AppSpacing.paddingMd,
      itemCount: history.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, index) {
        final exec = history[index];
        return Semantics(
          button: true,
          child: Card(
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.sm,
              ),
              leading: Semantics(
                container: true,
                child: _executionStatusIcon(exec.status),
              ),
              title: Text('Execution ${exec.id.substring(0, 8)}',
                  style: context.textTheme.titleSmall),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Started: ${exec.startedAt.formatRelative()}',
                      style: context.textTheme.bodySmall),
                  if (exec.completedAt != null)
                    Text('Completed: ${exec.completedAt!.formatRelative()}',
                        style: context.textTheme.bodySmall),
                  if (exec.errorMessage != null)
                    Text(exec.errorMessage!,
                        style: context.textTheme.bodySmall?.copyWith(color: AppTheme.error)),
                ],
              ),
              trailing: _statusBadge(exec.status),
            ),
          ),
        );
      },
    );
  }

  Widget _executionStatusIcon(ExecutionStatus status) {
    return Icon(
      switch (status) {
        ExecutionStatus.running => Icons.sync,
        ExecutionStatus.completed => Icons.check_circle,
        ExecutionStatus.failed => Icons.error,
        ExecutionStatus.cancelled => Icons.cancel,
      },
      color: switch (status) {
        ExecutionStatus.running => AppTheme.primary,
        ExecutionStatus.completed => AppTheme.success,
        ExecutionStatus.failed => AppTheme.error,
        ExecutionStatus.cancelled => Colors.grey,
      },
    );
  }

  Widget _statusBadge(ExecutionStatus status) {
    final (label, color) = switch (status) {
      ExecutionStatus.running => ('Running', AppTheme.primary),
      ExecutionStatus.completed => ('Completed', AppTheme.success),
      ExecutionStatus.failed => ('Failed', AppTheme.error),
      ExecutionStatus.cancelled => ('Cancelled', Colors.grey),
    };

    return Semantics(
      label: 'Status: $label',
      container: true,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 2),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
        ),
        child: Text(
          label,
          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color),
        ),
      ),
    );
  }
}
