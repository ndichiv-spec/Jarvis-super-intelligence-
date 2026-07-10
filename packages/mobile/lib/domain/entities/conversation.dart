import 'package:equatable/equatable.dart';

class Conversation extends Equatable {
  final String id;
  final String title;
  final String? projectId;
  final String? workspaceId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int messageCount;
  final bool isArchived;

  const Conversation({
    required this.id,
    required this.title,
    this.projectId,
    this.workspaceId,
    required this.createdAt,
    required this.updatedAt,
    required this.messageCount,
    required this.isArchived,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        projectId,
        workspaceId,
        createdAt,
        updatedAt,
        messageCount,
        isArchived,
      ];
}
