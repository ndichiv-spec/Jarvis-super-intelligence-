import 'package:jarvis_mobile/domain/entities/memory_item.dart';

class MemoryItemModel {
  final String id;
  final String content;
  final String type;
  final String source;
  final int importance;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool isArchived;

  const MemoryItemModel({
    required this.id,
    required this.content,
    required this.type,
    required this.source,
    required this.importance,
    required this.createdAt,
    required this.updatedAt,
    required this.isArchived,
  });

  factory MemoryItemModel.fromJson(Map<String, dynamic> json) {
    return MemoryItemModel(
      id: json['id'] as String,
      content: json['content'] as String,
      type: json['type'] as String,
      source: json['source'] as String,
      importance: json['importance'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      isArchived: json['isArchived'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'type': type,
      'source': source,
      'importance': importance,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'isArchived': isArchived,
    };
  }

  MemoryItem toEntity() {
    return MemoryItem(
      id: id,
      content: content,
      type: type,
      source: source,
      importance: importance,
      createdAt: createdAt,
      updatedAt: updatedAt,
      isArchived: isArchived,
    );
  }

  factory MemoryItemModel.fromEntity(MemoryItem entity) {
    return MemoryItemModel(
      id: entity.id,
      content: entity.content,
      type: entity.type,
      source: entity.source,
      importance: entity.importance,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
      isArchived: entity.isArchived,
    );
  }
}
