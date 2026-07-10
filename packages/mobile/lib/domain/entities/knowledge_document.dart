import 'package:equatable/equatable.dart';

class KnowledgeDocument extends Equatable {
  final String id;
  final String title;
  final String? summary;
  final String? collectionId;
  final String documentType;
  final int? fileSize;
  final DateTime createdAt;
  final DateTime updatedAt;

  const KnowledgeDocument({
    required this.id,
    required this.title,
    this.summary,
    this.collectionId,
    required this.documentType,
    this.fileSize,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        summary,
        collectionId,
        documentType,
        fileSize,
        createdAt,
        updatedAt,
      ];
}
