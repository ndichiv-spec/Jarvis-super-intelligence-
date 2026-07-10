import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';

class ConversationTile extends StatelessWidget {
  const ConversationTile({
    super.key,
    required this.conversation,
    this.lastMessagePreview,
    this.onTap,
  });

  final Conversation conversation;
  final String? lastMessagePreview;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Conversation: ${conversation.title}',
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: context.colorScheme.primaryContainer,
          radius: 20,
          child: Icon(
            Icons.chat_rounded,
            size: AppSpacing.iconSm,
            color: context.colorScheme.onPrimaryContainer,
          ),
        ),
        title: Text(
          conversation.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: context.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Row(
          children: [
            Expanded(
              child: Text(
                lastMessagePreview ?? 'No messages yet',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: context.textTheme.bodySmall?.copyWith(
                  color: context.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            if (conversation.messageCount > 0) ...[
              const SizedBox(width: AppSpacing.sm),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.sm,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: context.colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusXs),
                ),
                child: Text(
                  '${conversation.messageCount}',
                  style: context.textTheme.labelSmall?.copyWith(
                    color: context.colorScheme.onPrimaryContainer,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ],
        ),
        trailing: Text(
          conversation.updatedAt.formatRelative(),
          style: context.textTheme.labelSmall?.copyWith(
            color: context.colorScheme.onSurfaceVariant,
          ),
        ),
        onTap: onTap,
      ),
    );
  }
}
