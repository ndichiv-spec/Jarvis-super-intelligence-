import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/automation_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/entities/workflow_execution.dart';
import 'package:jarvis_mobile/domain/repositories/automation_repository.dart';

class AutomationRepositoryImpl implements AutomationRepository {
  AutomationRepositoryImpl({required this.remoteDataSource});

  final AutomationRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<Workflow>>> listWorkflows() async {
    try {
      final models = await remoteDataSource.listWorkflows();
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Workflow>> getWorkflow(String id) async {
    try {
      final model = await remoteDataSource.getWorkflow(id);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<WorkflowExecution>>> getHistory({String? workflowId, int page = 1, int limit = 20}) async {
    try {
      final models = await remoteDataSource.getHistory(workflowId: workflowId, page: page, limit: limit);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> pauseWorkflow(String id) async {
    try {
      await remoteDataSource.pauseWorkflow(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> resumeWorkflow(String id) async {
    try {
      await remoteDataSource.resumeWorkflow(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> cancelExecution(String id) async {
    try {
      await remoteDataSource.cancelExecution(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
