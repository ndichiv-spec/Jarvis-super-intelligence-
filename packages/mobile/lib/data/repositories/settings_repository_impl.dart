import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/settings_remote_datasource.dart';
import 'package:jarvis_mobile/data/models/app_settings_model.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/repositories/settings_repository.dart';

class SettingsRepositoryImpl implements SettingsRepository {
  SettingsRepositoryImpl({required this.remoteDataSource});

  final SettingsRemoteDataSource remoteDataSource;

  @override
  Future<Result<AppSettings>> get() async {
    try {
      final model = await remoteDataSource.get();
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> update(AppSettings settings) async {
    try {
      await remoteDataSource.update(AppSettingsModel.fromEntity(settings));
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
