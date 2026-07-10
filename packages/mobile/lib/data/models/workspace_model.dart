import 'package:jarvis_mobile/domain/entities/workspace.dart';

class WorkspaceModel {
  final String id;
  final String name;
  final String? description;
  final String role;
  final int memberCount;

  const WorkspaceModel({
    required this.id,
    required this.name,
    this.description,
    required this.role,
    required this.memberCount,
  });

  factory WorkspaceModel.fromJson(Map<String, dynamic> json) {
    return WorkspaceModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      role: json['role'] as String,
      memberCount: json['memberCount'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'role': role,
      'memberCount': memberCount,
    };
  }

  Workspace toEntity() {
    return Workspace(
      id: id,
      name: name,
      description: description,
      role: role,
      memberCount: memberCount,
    );
  }

  factory WorkspaceModel.fromEntity(Workspace entity) {
    return WorkspaceModel(
      id: entity.id,
      name: entity.name,
      description: entity.description,
      role: entity.role,
      memberCount: entity.memberCount,
    );
  }
}
