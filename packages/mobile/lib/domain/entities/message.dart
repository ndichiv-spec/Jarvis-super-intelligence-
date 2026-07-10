import 'package:equatable/equatable.dart';
import 'attachment.dart';

enum MessageRole { user, assistant, system }

class Message extends Equatable {
  final String id;
  final String conversationId;
  final MessageRole role;
  final String content;
  final List<Attachment> attachments;
  final DateTime createdAt;
  final Map<String, dynamic>? metadata;

  const Message({
    required this.id,
    required this.conversationId,
    required this.role,
    required this.content,
    this.attachments = const [],
    required this.createdAt,
    this.metadata,
  });

  @override
  List<Object?> get props => [
        id,
        conversationId,
        role,
        content,
        attachments,
        createdAt,
        metadata,
      ];
}
