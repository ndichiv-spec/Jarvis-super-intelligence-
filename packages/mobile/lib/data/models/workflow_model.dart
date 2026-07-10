import 'package:jarvis_mobile/domain/entities/workflow.dart';

class WorkflowModel {
  final String id;
  final String name;
  final String? description;
  final String status;
  final String? trigger;
  final DateTime? lastRunAt;
  final DateTime? nextRunAt;
  final DateTime createdAt;

  const WorkflowModel({
    required this.id,
    required this.name,
    this.description,
    required this.status,
    this.trigger,
    this.lastRunAt,
    this.nextRunAt,
    required this.createdAt,
  });

  factory WorkflowModel.fromJson(Map<String, dynamic> json) {
    return WorkflowModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      status: json['status'] as String,
      trigger: json['trigger'] as String?,
      lastRunAt: json['lastRunAt'] != null ? DateTime.parse(json['lastRunAt'] as String) : null,
      nextRunAt: json['nextRunAt'] != null ? DateTime.parse(json['nextRunAt'] as String) : null,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'status': status,
      'trigger': trigger,
      'lastRunAt': lastRunAt?.toIso8601String(),
      'nextRunAt': nextRunAt?.toIso8601String(),
      'createdAt': createdAt.toIso8601String(),
    };
  }

  Workflow toEntity() {
    return Workflow(
      id: id,
      name: name,
      description: description,
      status: WorkflowStatus.values.firstWhere(
        (e) => e.name == status,
        orElse: () => WorkflowStatus.idle,
      ),
      trigger: trigger,
      lastRunAt: lastRunAt,
      nextRunAt: nextRunAt,
      createdAt: createdAt,
    );
  }

  factory WorkflowModel.fromEntity(Workflow entity) {
    return WorkflowModel(
      id: entity.id,
      name: entity.name,
      description: entity.description,
      status: entity.status.name,
      trigger: entity.trigger,
      lastRunAt: entity.lastRunAt,
      nextRunAt: entity.nextRunAt,
      createdAt: entity.createdAt,
    );
  }
}
