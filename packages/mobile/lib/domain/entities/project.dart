import 'package:equatable/equatable.dart';

class Project extends Equatable {
  final String id;
  final String name;
  final String? description;
  final String status;
  final double progress;
  final String? workspaceId;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Project({
    required this.id,
    required this.name,
    this.description,
    required this.status,
    required this.progress,
    this.workspaceId,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        status,
        progress,
        workspaceId,
        createdAt,
        updatedAt,
      ];
}
