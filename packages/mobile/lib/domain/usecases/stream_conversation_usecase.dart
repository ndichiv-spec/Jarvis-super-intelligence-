import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/repositories/conversation_repository.dart';

class StreamConversationUseCase {
  final ConversationRepository _conversationRepository;

  StreamConversationUseCase(this._conversationRepository);

  Stream<Conversation> call(String id) {
    return _conversationRepository.streamConversation(id);
  }
}
