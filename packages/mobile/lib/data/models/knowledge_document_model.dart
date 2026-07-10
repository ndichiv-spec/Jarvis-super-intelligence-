import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';

class KnowledgeDocumentModel {
  final String id;
  final String title;
  final String? summary;
  final String? collectionId;
  final String documentType;
  final int? fileSize;
  final DateTime createdAt;
  final DateTime updatedAt;

  const KnowledgeDocumentModel({
    required this.id,
    required this.title,
    this.summary,
    this.collectionId,
    required this.documentType,
    this.fileSize,
    required this.createdAt,
    required this.updatedAt,
  });

  factory KnowledgeDocumentModel.fromJson(Map<String, dynamic> json) {
    return KnowledgeDocumentModel(
      id: json['id'] as String,
      title: json['title'] as String,
      summary: json['summary'] as String?,
      collectionId: json['collectionId'] as String?,
      documentType: json['documentType'] as String,
      fileSize: json['fileSize'] as int?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'summary': summary,
      'collectionId': collectionId,
      'documentType': documentType,
      'fileSize': fileSize,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }

  KnowledgeDocument toEntity() {
    return KnowledgeDocument(
      id: id,
      title: title,
      summary: summary,
      collectionId: collectionId,
      documentType: documentType,
      fileSize: fileSize,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }

  factory KnowledgeDocumentModel.fromEntity(KnowledgeDocument entity) {
    return KnowledgeDocumentModel(
      id: entity.id,
      title: entity.title,
      summary: entity.summary,
      collectionId: entity.collectionId,
      documentType: entity.documentType,
      fileSize: entity.fileSize,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
}
