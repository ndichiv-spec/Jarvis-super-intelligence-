import 'package:equatable/equatable.dart';

enum WorkflowStatus { idle, running, paused, completed, failed }

class Workflow extends Equatable {
  final String id;
  final String name;
  final String? description;
  final WorkflowStatus status;
  final String? trigger;
  final DateTime? lastRunAt;
  final DateTime? nextRunAt;
  final DateTime createdAt;

  const Workflow({
    required this.id,
    required this.name,
    this.description,
    required this.status,
    this.trigger,
    this.lastRunAt,
    this.nextRunAt,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        status,
        trigger,
        lastRunAt,
        nextRunAt,
        createdAt,
      ];
}
