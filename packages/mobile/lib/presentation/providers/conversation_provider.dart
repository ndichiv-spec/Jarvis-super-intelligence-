import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/message.dart';
import 'package:jarvis_mobile/domain/repositories/conversation_repository.dart';
import 'package:jarvis_mobile/domain/usecases/get_conversations_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/send_message_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/stream_conversation_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class ConversationState {
  final List<Conversation> conversations;
  final Conversation? currentConversation;
  final List<Message> messages;
  final bool isLoading;
  final bool isStreaming;

  const ConversationState({
    this.conversations = const [],
    this.currentConversation,
    this.messages = const [],
    this.isLoading = false,
    this.isStreaming = false,
  });

  ConversationState copyWith({
    List<Conversation>? conversations,
    Conversation? currentConversation,
    List<Message>? messages,
    bool? isLoading,
    bool? isStreaming,
  }) {
    return ConversationState(
      conversations: conversations ?? this.conversations,
      currentConversation: currentConversation ?? this.currentConversation,
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      isStreaming: isStreaming ?? this.isStreaming,
    );
  }
}

class ConversationNotifier extends StateNotifier<ConversationState> {
  final GetConversationsUseCase _getConversationsUseCase;
  final SendMessageUseCase _sendMessageUseCase;
  final StreamConversationUseCase _streamConversationUseCase;
  final ConversationRepository _conversationRepository;
  StreamSubscription<Conversation>? _streamSubscription;

  ConversationNotifier({
    required GetConversationsUseCase getConversationsUseCase,
    required SendMessageUseCase sendMessageUseCase,
    required StreamConversationUseCase streamConversationUseCase,
    required ConversationRepository conversationRepository,
  })  : _getConversationsUseCase = getConversationsUseCase,
        _sendMessageUseCase = sendMessageUseCase,
        _streamConversationUseCase = streamConversationUseCase,
        _conversationRepository = conversationRepository,
        super(const ConversationState());

  @override
  void dispose() {
    _streamSubscription?.cancel();
    super.dispose();
  }

  Future<void> list(String workspaceId) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _getConversationsUseCase.call(workspaceId);
      switch (result) {
        case Success<List<Conversation>>():
          state = state.copyWith(conversations: result.data, isLoading: false);
        case Failure<List<Conversation>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> select(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _conversationRepository.get(id);
      switch (result) {
        case Success<Conversation>():
          state = state.copyWith(currentConversation: result.data, isLoading: false);
        case Failure<Conversation>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> create(String title) async {
    try {
      final result = await _conversationRepository.create(title);
      if (result is Success<Conversation>) {
        state = state.copyWith(
          conversations: [result.data, ...state.conversations],
          currentConversation: result.data,
        );
      }
    } catch (_) {}
  }

  Future<void> sendMessage({
    required String conversationId,
    required String content,
    List<String>? attachmentIds,
  }) async {
    try {
      final result = await _sendMessageUseCase.call(
        conversationId: conversationId,
        content: content,
        attachmentIds: attachmentIds,
      );
      if (result is Success<Message>) {
        state = state.copyWith(
          messages: [...state.messages, result.data],
        );
      }
    } catch (_) {}
  }

  void streamConversation(String id) {
    _streamSubscription?.cancel();
    state = state.copyWith(isStreaming: true);
    _streamSubscription = _streamConversationUseCase.call(id).listen(
      (conversation) {
        state = state.copyWith(
          currentConversation: conversation,
          isStreaming: false,
        );
      },
      onError: (_) {
        state = state.copyWith(isStreaming: false);
      },
      onDone: () {
        state = state.copyWith(isStreaming: false);
      },
    );
  }

  void cancelStreaming() {
    _streamSubscription?.cancel();
    state = state.copyWith(isStreaming: false);
  }
}

final conversationProvider =
    StateNotifierProvider<ConversationNotifier, ConversationState>((ref) {
  return ConversationNotifier(
    getConversationsUseCase: ref.watch(getConversationsUseCaseProvider),
    sendMessageUseCase: ref.watch(sendMessageUseCaseProvider),
    streamConversationUseCase: ref.watch(streamConversationUseCaseProvider),
    conversationRepository: ref.watch(conversationRepositoryProvider),
  );
});
