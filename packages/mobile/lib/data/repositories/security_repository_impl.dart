import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/security_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/device.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/repositories/security_repository.dart';

class SecurityRepositoryImpl implements SecurityRepository {
  SecurityRepositoryImpl({required this.remoteDataSource});

  final SecurityRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<Session>>> listSessions() async {
    try {
      final models = await remoteDataSource.listSessions();
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> revokeSession(String id) async {
    try {
      await remoteDataSource.revokeSession(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<Device>>> listDevices() async {
    try {
      final models = await remoteDataSource.listDevices();
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Device>> registerDevice(String name, String type) async {
    try {
      final model = await remoteDataSource.registerDevice(name, type);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> trustDevice(String id) async {
    try {
      await remoteDataSource.trustDevice(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> removeDevice(String id) async {
    try {
      await remoteDataSource.removeDevice(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
