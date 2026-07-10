import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/workspace_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/workspace.dart';
import 'package:jarvis_mobile/domain/repositories/workspace_repository.dart';

class WorkspaceRepositoryImpl implements WorkspaceRepository {
  WorkspaceRepositoryImpl({required this.remoteDataSource});

  final WorkspaceRemoteDataSource remoteDataSource;

  @override
  Future<Result<Workspace>> getCurrent() async {
    try {
      final model = await remoteDataSource.getCurrent();
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<Workspace>>> list() async {
    try {
      final models = await remoteDataSource.list();
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> setCurrent(String id) async {
    try {
      await remoteDataSource.setCurrent(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
