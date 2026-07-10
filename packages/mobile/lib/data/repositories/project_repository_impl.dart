import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/project_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/entities/project.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/repositories/project_repository.dart';

class ProjectRepositoryImpl implements ProjectRepository {
  ProjectRepositoryImpl({required this.remoteDataSource});

  final ProjectRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<Project>>> list(String workspaceId) async {
    try {
      final models = await remoteDataSource.list(workspaceId);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Project>> get(String id) async {
    try {
      final model = await remoteDataSource.get(id);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<Conversation>>> getConversations(String projectId) async {
    try {
      final models = await remoteDataSource.getConversations(projectId);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<Workflow>>> getWorkflows(String projectId) async {
    try {
      final models = await remoteDataSource.getWorkflows(projectId);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<KnowledgeDocument>>> getKnowledge(String projectId) async {
    try {
      final models = await remoteDataSource.getKnowledge(projectId);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
