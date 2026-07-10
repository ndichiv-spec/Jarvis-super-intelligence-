import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/presentation/providers/conversation_provider.dart';
import 'package:jarvis_mobile/presentation/widgets/empty_state.dart';
import 'package:jarvis_mobile/presentation/widgets/search_bar_widget.dart';

class AiWorkspacePage extends ConsumerStatefulWidget {
  const AiWorkspacePage({super.key});

  @override
  ConsumerState<AiWorkspacePage> createState() => _AiWorkspacePageState();
}

class _AiWorkspacePageState extends ConsumerState<AiWorkspacePage> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;
    final convId = ref.read(conversationProvider).currentConversation?.id ?? '';
    ref.read(conversationProvider.notifier).sendMessage(
      conversationId: convId,
      content: text,
    );
    _messageController.clear();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(conversationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Workspace'),
        actions: [
          Semantics(
            button: true,
            label: 'New conversation',
            child: IconButton(
              icon: const Icon(Icons.add_comment_outlined),
              tooltip: 'New conversation',
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (ctx) => _NewConversationDialog(),
                );
              },
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          if (state.conversations.isNotEmpty)
            SizedBox(
              height: 48,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: AppSpacing.horizontalMd,
                itemCount: state.conversations.length,
                itemBuilder: (_, i) {
                  final c = state.conversations[i];
                  final isSelected = c.id == state.currentConversation?.id;
                  return Padding(
                    padding: const EdgeInsets.only(right: AppSpacing.sm),
                    child: Semantics(
                      button: true,
                      selected: isSelected,
                      label: c.title,
                      child: FilterChip(
                        label: Text(c.title, style: const TextStyle(fontSize: 12)),
                        selected: isSelected,
                        onSelected: (_) => ref.read(conversationProvider.notifier).select(c.id),
                      ),
                    ),
                  );
                },
              ),
            ),
          const Divider(height: 1),
          Expanded(
            child: state.messages.isEmpty
                ? const EmptyState(
                    message: 'Start a conversation with JARVIS',
                    icon: Icons.chat_bubble_outline_rounded,
                  )
                : ListView.builder(
                    controller: _scrollController,
                    padding: AppSpacing.paddingMd,
                    itemCount: state.messages.length,
                    itemBuilder: (_, i) {
                      final msg = state.messages[i];
                      final isUser = msg.role == MessageRole.user;
                      return Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                        child: Semantics(
                          label: '${isUser ? "You" : "JARVIS"}: ${msg.content}',
                          child: Row(
                            mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              if (!isUser)
                                CircleAvatar(
                                  radius: 14,
                                  backgroundColor: context.colorScheme.primaryContainer,
                                  child: Icon(Icons.psychology, size: 16, color: context.colorScheme.onPrimaryContainer),
                                ),
                              const SizedBox(width: AppSpacing.sm),
                              Flexible(
                                child: Container(
                                  constraints: BoxConstraints(maxWidth: context.screenWidth * 0.7),
                                  padding: const EdgeInsets.all(AppSpacing.md),
                                  decoration: BoxDecoration(
                                    color: isUser
                                        ? context.colorScheme.primary
                                        : context.colorScheme.surfaceContainerHighest,
                                    borderRadius: BorderRadius.circular(
                                      AppSpacing.radiusMd,
                                    ).copyWith(
                                      bottomLeft: isUser ? const Radius.circular(AppSpacing.radiusMd) : Radius.zero,
                                      bottomRight: isUser ? Radius.zero : const Radius.circular(AppSpacing.radiusMd),
                                    ),
                                  ),
                                  child: Text(
                                    msg.content,
                                    style: TextStyle(
                                      color: isUser
                                          ? context.colorScheme.onPrimary
                                          : context.colorScheme.onSurface,
                                    ),
                                  ),
                                ),
                              ),
                              if (isUser)
                                const SizedBox(width: AppSpacing.sm),
                              if (isUser)
                                CircleAvatar(
                                  radius: 14,
                                  backgroundColor: context.colorScheme.secondaryContainer,
                                  child: Icon(Icons.person, size: 16, color: context.colorScheme.onSecondaryContainer),
                                ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
          if (state.isStreaming)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.sm),
              child: LinearProgressIndicator(),
            ),
          Container(
            decoration: BoxDecoration(
              color: context.colorScheme.surface,
              border: Border(top: BorderSide(color: context.colorScheme.outlineVariant)),
            ),
            padding: AppSpacing.paddingMd.copyWith(bottom: MediaQuery.of(context).padding.bottom + AppSpacing.md),
            child: SafeArea(
              top: false,
              child: Row(
                children: [
                  Semantics(
                    button: true,
                    label: 'Attach file',
                    child: IconButton(
                      icon: const Icon(Icons.attach_file_outlined),
                      onPressed: () {},
                    ),
                  ),
                  Expanded(
                    child: Semantics(
                      label: 'Message input',
                      child: TextField(
                        controller: _messageController,
                        textInputAction: TextInputAction.send,
                        onSubmitted: (_) => _sendMessage(),
                        decoration: const InputDecoration(
                          hintText: 'Message JARVIS...',
                          border: InputBorder.none,
                          filled: false,
                          contentPadding: EdgeInsets.symmetric(vertical: 10),
                        ),
                      ),
                    ),
                  ),
                  Semantics(
                    button: true,
                    label: 'Send message',
                    child: IconButton(
                      icon: const Icon(Icons.send_rounded),
                      color: context.colorScheme.primary,
                      onPressed: _sendMessage,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NewConversationDialog extends ConsumerStatefulWidget {
  @override
  ConsumerState<_NewConversationDialog> createState() => _NewConversationDialogState();
}

class _NewConversationDialogState extends ConsumerState<_NewConversationDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('New Conversation'),
      content: Semantics(
        label: 'Conversation title',
        child: TextField(
          controller: _controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Conversation title'),
          onSubmitted: (_) => _create(),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(onPressed: _create, child: const Text('Create')),
      ],
    );
  }

  void _create() {
    final title = _controller.text.trim();
    if (title.isNotEmpty) {
      ref.read(conversationProvider.notifier).create(title);
      Navigator.pop(context);
    }
  }
}
