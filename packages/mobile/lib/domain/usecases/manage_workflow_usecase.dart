import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/repositories/automation_repository.dart';

class ManageWorkflowUseCase {
  final AutomationRepository _automationRepository;

  ManageWorkflowUseCase(this._automationRepository);

  Future<Result<void>> pause(String workflowId) {
    return _automationRepository.pauseWorkflow(workflowId);
  }

  Future<Result<void>> resume(String workflowId) {
    return _automationRepository.resumeWorkflow(workflowId);
  }

  Future<Result<void>> cancel(String executionId) {
    return _automationRepository.cancelExecution(executionId);
  }
}
