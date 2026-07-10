import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/auth_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/entities/user.dart';
import 'package:jarvis_mobile/domain/repositories/auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl({required this.remoteDataSource});

  final AuthRemoteDataSource remoteDataSource;

  @override
  Future<Result<Session>> login(String email, String password) async {
    try {
      final model = await remoteDataSource.login(email, password);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Session>> loginWithBiometric() async {
    try {
      final model = await remoteDataSource.loginWithBiometric();
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> logout() async {
    try {
      await remoteDataSource.logout();
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Session>> refreshSession() async {
    try {
      final model = await remoteDataSource.refreshSession();
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Session?>> getSession() async {
    try {
      final model = await remoteDataSource.getSession();
      return Result.success(model?.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<bool>> isAuthenticated() async {
    try {
      final session = await remoteDataSource.getSession();
      return Result.success(session != null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
