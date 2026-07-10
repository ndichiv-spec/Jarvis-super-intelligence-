import 'package:jarvis_mobile/domain/entities/knowledge_collection.dart';

class KnowledgeCollectionModel {
  final String id;
  final String name;
  final String? description;
  final int documentCount;
  final DateTime createdAt;

  const KnowledgeCollectionModel({
    required this.id,
    required this.name,
    this.description,
    required this.documentCount,
    required this.createdAt,
  });

  factory KnowledgeCollectionModel.fromJson(Map<String, dynamic> json) {
    return KnowledgeCollectionModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      documentCount: json['documentCount'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'documentCount': documentCount,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  KnowledgeCollection toEntity() {
    return KnowledgeCollection(
      id: id,
      name: name,
      description: description,
      documentCount: documentCount,
      createdAt: createdAt,
    );
  }

  factory KnowledgeCollectionModel.fromEntity(KnowledgeCollection entity) {
    return KnowledgeCollectionModel(
      id: entity.id,
      name: entity.name,
      description: entity.description,
      documentCount: entity.documentCount,
      createdAt: entity.createdAt,
    );
  }
}
