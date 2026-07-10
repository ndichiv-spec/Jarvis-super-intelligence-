import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/entities/workflow_execution.dart';

abstract class AutomationRepository {
  Future<Result<List<Workflow>>> listWorkflows();
  Future<Result<Workflow>> getWorkflow(String id);
  Future<Result<List<WorkflowExecution>>> getHistory({String? workflowId, int page = 1, int limit = 20});
  Future<Result<void>> pauseWorkflow(String id);
  Future<Result<void>> resumeWorkflow(String id);
  Future<Result<void>> cancelExecution(String id);
}
