import 'package:jarvis_mobile/domain/entities/project.dart';

class ProjectModel {
  final String id;
  final String name;
  final String? description;
  final String status;
  final double progress;
  final String? workspaceId;
  final DateTime createdAt;
  final DateTime updatedAt;

  const ProjectModel({
    required this.id,
    required this.name,
    this.description,
    required this.status,
    required this.progress,
    this.workspaceId,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ProjectModel.fromJson(Map<String, dynamic> json) {
    return ProjectModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      status: json['status'] as String,
      progress: (json['progress'] as num).toDouble(),
      workspaceId: json['workspaceId'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'status': status,
      'progress': progress,
      'workspaceId': workspaceId,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }

  Project toEntity() {
    return Project(
      id: id,
      name: name,
      description: description,
      status: status,
      progress: progress,
      workspaceId: workspaceId,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }

  factory ProjectModel.fromEntity(Project entity) {
    return ProjectModel(
      id: entity.id,
      name: entity.name,
      description: entity.description,
      status: entity.status,
      progress: entity.progress,
      workspaceId: entity.workspaceId,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
    );
  }
}
