import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/presentation/widgets/status_badge.dart';

class WorkflowTile extends StatelessWidget {
  const WorkflowTile({
    super.key,
    required this.workflow,
    this.onTap,
    this.onPause,
    this.onResume,
  });

  final Workflow workflow;
  final VoidCallback? onTap;
  final VoidCallback? onPause;
  final VoidCallback? onResume;

  String _triggerLabel(String? trigger) {
    if (trigger == null) return 'Manual';
    switch (trigger.toLowerCase()) {
      case 'schedule':
      case 'cron':
        return 'Scheduled';
      case 'event':
      case 'webhook':
        return 'Webhook';
      case 'manual':
        return 'Manual';
      default:
        return trigger;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Workflow: ${workflow.name}',
      child: Card(
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          child: Padding(
            padding: AppSpacing.paddingMd,
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              workflow.name,
                              style: context.textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.xs),
                      Row(
                        children: [
                          StatusBadge(status: workflow.status.name),
                          const SizedBox(width: AppSpacing.sm),
                          Icon(
                            Icons.touch_app_rounded,
                            size: 12,
                            color: context.colorScheme.onSurfaceVariant,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            _triggerLabel(workflow.trigger),
                            style: context.textTheme.bodySmall?.copyWith(
                              color: context.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                      if (workflow.lastRunAt != null) ...[
                        const SizedBox(height: AppSpacing.xs),
                        Text(
                          'Last run ${workflow.lastRunAt!.formatRelative()}',
                          style: context.textTheme.bodySmall?.copyWith(
                            color: context.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                if (workflow.status == WorkflowStatus.running && onPause != null)
                  IconButton(
                    icon: const Icon(Icons.pause_rounded),
                    tooltip: 'Pause',
                    onPressed: onPause,
                  ),
                if (workflow.status == WorkflowStatus.paused && onResume != null)
                  IconButton(
                    icon: const Icon(Icons.play_arrow_rounded),
                    tooltip: 'Resume',
                    onPressed: onResume,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
