import 'package:equatable/equatable.dart';

enum ExecutionStatus { running, completed, failed, cancelled }

class WorkflowExecution extends Equatable {
  final String id;
  final String workflowId;
  final ExecutionStatus status;
  final DateTime startedAt;
  final DateTime? completedAt;
  final String? errorMessage;

  const WorkflowExecution({
    required this.id,
    required this.workflowId,
    required this.status,
    required this.startedAt,
    this.completedAt,
    this.errorMessage,
  });

  @override
  List<Object?> get props => [
        id,
        workflowId,
        status,
        startedAt,
        completedAt,
        errorMessage,
      ];
}
