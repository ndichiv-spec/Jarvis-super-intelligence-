import 'package:equatable/equatable.dart';

class MemoryItem extends Equatable {
  final String id;
  final String content;
  final String type;
  final String source;
  final int importance;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool isArchived;

  const MemoryItem({
    required this.id,
    required this.content,
    required this.type,
    required this.source,
    required this.importance,
    required this.createdAt,
    required this.updatedAt,
    required this.isArchived,
  });

  @override
  List<Object?> get props => [
        id,
        content,
        type,
        source,
        importance,
        createdAt,
        updatedAt,
        isArchived,
      ];
}
