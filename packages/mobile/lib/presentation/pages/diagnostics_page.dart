import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/presentation/providers/diagnostics_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/metric_card.dart';

class DiagnosticsPage extends ConsumerStatefulWidget {
  const DiagnosticsPage({super.key});

  @override
  ConsumerState<DiagnosticsPage> createState() => _DiagnosticsPageState();
}

class _DiagnosticsPageState extends ConsumerState<DiagnosticsPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(diagnosticsProvider.notifier).loadAll();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diagnosticsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Diagnostics'),
        actions: [
          Semantics(
            button: true,
            label: 'Refresh diagnostics',
            child: IconButton(
              icon: const Icon(Icons.refresh_rounded),
              tooltip: 'Refresh',
              onPressed: () => ref.read(diagnosticsProvider.notifier).loadAll(),
            ),
          ),
        ],
      ),
      body: state.isLoading && state.health == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: AppSpacing.paddingMd,
              children: [
                _SectionTitle('Gateway Connectivity'),
                const SizedBox(height: AppSpacing.sm),
                _StatusRow(
                  label: 'Gateway',
                  connected: state.connectivityInfo['gateway'] ?? false,
                ),
                _StatusRow(
                  label: 'WebSocket',
                  connected: state.connectivityInfo['websocket'] ?? false,
                ),
                _StatusRow(
                  label: 'Device',
                  connected: state.connectivityInfo['device'] ?? false,
                ),
                const SizedBox(height: AppSpacing.lg),
                _SectionTitle('Application Health'),
                const SizedBox(height: AppSpacing.sm),
                if (state.health != null) ...[
                  Card(
                    child: Padding(
                      padding: AppSpacing.paddingMd,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _DetailRow('Status', state.health!.status.name),
                          _DetailRow('Version', state.health!.version),
                          _DetailRow('Last Checked', state.health!.lastCheckedAt.formatRelative()),
                        ],
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: AppSpacing.lg),
                _SectionTitle('Synchronization'),
                const SizedBox(height: AppSpacing.sm),
                if (state.syncStatus != null) ...[
                  Card(
                    child: Padding(
                      padding: AppSpacing.paddingMd,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _DetailRow('Status', state.syncStatus!.isSyncing ? 'Syncing' : 'Idle'),
                          if (state.syncStatus!.lastSyncedAt != null)
                            _DetailRow('Last Synced', state.syncStatus!.lastSyncedAt!.formatRelative()),
                          _DetailRow('Pending Items', '${state.syncStatus!.pendingItems}'),
                          _DetailRow('Failed Items', '${state.syncStatus!.failedItems}'),
                        ],
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: AppSpacing.lg),
                _SectionTitle('Offline Queue'),
                const SizedBox(height: AppSpacing.sm),
                Card(
                  child: Padding(
                    padding: AppSpacing.paddingMd,
                    child: state.offlineQueue.isEmpty
                        ? Text('No queued actions',
                            style: TextStyle(color: context.colorScheme.onSurfaceVariant))
                        : Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: state.offlineQueue.map((item) {
                              return Text(
                                '${item['action_type']} (${item['status']})',
                                style: context.textTheme.bodySmall,
                              );
                            }).toList(),
                          ),
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                _SectionTitle('Version Information'),
                const SizedBox(height: AppSpacing.sm),
                Card(
                  child: Padding(
                    padding: AppSpacing.paddingMd,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _DetailRow('App Version', '1.0.0+1'),
                        _DetailRow('Flutter', '3.4+'),
                        _DetailRow('Dart SDK', '3.4+'),
                      ],
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;

  const _SectionTitle(this.title);

  @override
  Widget build(BuildContext context) {
    return Semantics(
      header: true,
      child: Text(
        title,
        style: context.textTheme.titleSmall?.copyWith(
          color: context.colorScheme.primary,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _StatusRow extends StatelessWidget {
  final String label;
  final bool connected;

  const _StatusRow({required this.label, required this.connected});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(
          connected ? Icons.check_circle : Icons.error,
          color: connected ? AppTheme.success : AppTheme.error,
        ),
        title: Text(label),
        trailing: Text(
          connected ? 'Connected' : 'Disconnected',
          style: TextStyle(
            color: connected ? AppTheme.success : AppTheme.error,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: context.textTheme.bodyMedium),
          Text(value, style: context.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
