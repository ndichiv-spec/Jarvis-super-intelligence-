import 'package:equatable/equatable.dart';

class KnowledgeCollection extends Equatable {
  final String id;
  final String name;
  final String? description;
  final int documentCount;
  final DateTime createdAt;

  const KnowledgeCollection({
    required this.id,
    required this.name,
    this.description,
    required this.documentCount,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [id, name, description, documentCount, createdAt];
}
