import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/quick_action_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/quick_action.dart';
import 'package:jarvis_mobile/domain/repositories/quick_action_repository.dart';

class QuickActionRepositoryImpl implements QuickActionRepository {
  QuickActionRepositoryImpl({required this.remoteDataSource});

  final QuickActionRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<QuickAction>>> list() async {
    try {
      final models = await remoteDataSource.list();
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> execute(String id) async {
    try {
      await remoteDataSource.execute(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> updateOrder(List<String> ids) async {
    try {
      await remoteDataSource.updateOrder(ids);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
