import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/notification_remote_datasource.dart';
import 'package:jarvis_mobile/data/models/app_settings_model.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart' as domain;
import 'package:jarvis_mobile/domain/repositories/notification_repository.dart';

class NotificationRepositoryImpl implements NotificationRepository {
  NotificationRepositoryImpl({required this.remoteDataSource});

  final NotificationRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<domain.Notification>>> list({int page = 1, int limit = 20}) async {
    try {
      final models = await remoteDataSource.list(page: page, limit: limit);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> markRead(String id) async {
    try {
      await remoteDataSource.markRead(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> markAllRead() async {
    try {
      await remoteDataSource.markAllRead();
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<AppSettings>> getSettings() async {
    try {
      final model = await remoteDataSource.getSettings();
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<void>> updateSettings(AppSettings settings) async {
    try {
      await remoteDataSource.updateSettings(AppSettingsModel.fromEntity(settings));
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
