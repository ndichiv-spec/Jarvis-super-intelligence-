import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/message.dart';

abstract class SendMessageUseCase {
  Future<Result<Message>> call({
    required String conversationId,
    required String content,
    List<String>? attachmentIds,
  });
}
