import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/memory_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/memory_item.dart';
import 'package:jarvis_mobile/domain/repositories/memory_repository.dart';

class MemoryRepositoryImpl implements MemoryRepository {
  MemoryRepositoryImpl({required this.remoteDataSource});

  final MemoryRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<MemoryItem>>> list({int page = 1, int limit = 20}) async {
    try {
      final models = await remoteDataSource.list(page: page, limit: limit);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<MemoryItem>>> search(String query) async {
    try {
      final models = await remoteDataSource.search(query);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<MemoryItem>> get(String id) async {
    try {
      final model = await remoteDataSource.get(id);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> archive(String id) async {
    try {
      await remoteDataSource.archive(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> delete(String id) async {
    try {
      await remoteDataSource.delete(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
