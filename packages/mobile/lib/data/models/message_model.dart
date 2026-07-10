import 'package:jarvis_mobile/domain/entities/message.dart';
import 'attachment_model.dart';

class MessageModel {
  final String id;
  final String conversationId;
  final String role;
  final String content;
  final List<AttachmentModel> attachments;
  final DateTime createdAt;
  final Map<String, dynamic>? metadata;

  const MessageModel({
    required this.id,
    required this.conversationId,
    required this.role,
    required this.content,
    this.attachments = const [],
    required this.createdAt,
    this.metadata,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'] as String,
      conversationId: json['conversationId'] as String,
      role: json['role'] as String,
      content: json['content'] as String,
      attachments: (json['attachments'] as List<dynamic>?)
              ?.map((e) => AttachmentModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      createdAt: DateTime.parse(json['createdAt'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'conversationId': conversationId,
      'role': role,
      'content': content,
      'attachments': attachments.map((e) => e.toJson()).toList(),
      'createdAt': createdAt.toIso8601String(),
      'metadata': metadata,
    };
  }

  Message toEntity() {
    return Message(
      id: id,
      conversationId: conversationId,
      role: MessageRole.values.firstWhere(
        (e) => e.name == role,
        orElse: () => MessageRole.user,
      ),
      content: content,
      attachments: attachments.map((e) => e.toEntity()).toList(),
      createdAt: createdAt,
      metadata: metadata,
    );
  }

  factory MessageModel.fromEntity(Message entity) {
    return MessageModel(
      id: entity.id,
      conversationId: entity.conversationId,
      role: entity.role.name,
      content: entity.content,
      attachments: entity.attachments.map((e) => AttachmentModel.fromEntity(e)).toList(),
      createdAt: entity.createdAt,
      metadata: entity.metadata,
    );
  }
}
