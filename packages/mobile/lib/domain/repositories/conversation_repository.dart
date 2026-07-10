import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';

abstract class ConversationRepository {
  Future<Result<List<Conversation>>> list(String workspaceId, {int page = 1, int limit = 20});
  Future<Result<Conversation>> get(String id);
  Future<Result<Conversation>> create(String title, {String? projectId});
  Future<Result<Message>> sendMessage({
    required String conversationId,
    required String content,
    List<String>? attachmentIds,
  });
  Stream<Conversation> streamConversation(String id);
  Future<Result<void>> delete(String id);
}
