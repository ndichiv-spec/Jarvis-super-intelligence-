import 'package:jarvis_mobile/domain/entities/workflow_execution.dart';

class WorkflowExecutionModel {
  final String id;
  final String workflowId;
  final String status;
  final DateTime startedAt;
  final DateTime? completedAt;
  final String? errorMessage;

  const WorkflowExecutionModel({
    required this.id,
    required this.workflowId,
    required this.status,
    required this.startedAt,
    this.completedAt,
    this.errorMessage,
  });

  factory WorkflowExecutionModel.fromJson(Map<String, dynamic> json) {
    return WorkflowExecutionModel(
      id: json['id'] as String,
      workflowId: json['workflowId'] as String,
      status: json['status'] as String,
      startedAt: DateTime.parse(json['startedAt'] as String),
      completedAt: json['completedAt'] != null ? DateTime.parse(json['completedAt'] as String) : null,
      errorMessage: json['errorMessage'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'workflowId': workflowId,
      'status': status,
      'startedAt': startedAt.toIso8601String(),
      'completedAt': completedAt?.toIso8601String(),
      'errorMessage': errorMessage,
    };
  }

  WorkflowExecution toEntity() {
    return WorkflowExecution(
      id: id,
      workflowId: workflowId,
      status: ExecutionStatus.values.firstWhere(
        (e) => e.name == status,
        orElse: () => ExecutionStatus.running,
      ),
      startedAt: startedAt,
      completedAt: completedAt,
      errorMessage: errorMessage,
    );
  }

  factory WorkflowExecutionModel.fromEntity(WorkflowExecution entity) {
    return WorkflowExecutionModel(
      id: entity.id,
      workflowId: entity.workflowId,
      status: entity.status.name,
      startedAt: entity.startedAt,
      completedAt: entity.completedAt,
      errorMessage: entity.errorMessage,
    );
  }
}
