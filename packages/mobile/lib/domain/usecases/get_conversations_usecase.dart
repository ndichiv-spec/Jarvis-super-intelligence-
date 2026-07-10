import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/repositories/conversation_repository.dart';

class GetConversationsUseCase {
  final ConversationRepository _conversationRepository;

  GetConversationsUseCase(this._conversationRepository);

  Future<Result<List<Conversation>>> call(
    String workspaceId, {
    int page = 1,
    int limit = 20,
  }) {
    return _conversationRepository.list(workspaceId, page: page, limit: limit);
  }
}
