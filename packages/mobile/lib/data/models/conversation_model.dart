import 'package:jarvis_mobile/domain/entities/conversation.dart';

class ConversationModel {
  final String id;
  final String title;
  final String? projectId;
  final String? workspaceId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int messageCount;
  final bool isArchived;

  const ConversationModel({
    required this.id,
    required this.title,
    this.projectId,
    this.workspaceId,
    required this.createdAt,
    required this.updatedAt,
    required this.messageCount,
    required this.isArchived,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      id: json['id'] as String,
      title: json['title'] as String,
      projectId: json['projectId'] as String?,
      workspaceId: json['workspaceId'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      messageCount: json['messageCount'] as int,
      isArchived: json['isArchived'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'projectId': projectId,
      'workspaceId': workspaceId,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'messageCount': messageCount,
      'isArchived': isArchived,
    };
  }

  Conversation toEntity() {
    return Conversation(
      id: id,
      title: title,
      projectId: projectId,
      workspaceId: workspaceId,
      createdAt: createdAt,
      updatedAt: updatedAt,
      messageCount: messageCount,
      isArchived: isArchived,
    );
  }

  factory ConversationModel.fromEntity(Conversation entity) {
    return ConversationModel(
      id: entity.id,
      title: entity.title,
      projectId: entity.projectId,
      workspaceId: entity.workspaceId,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
      messageCount: entity.messageCount,
      isArchived: entity.isArchived,
    );
  }
}
