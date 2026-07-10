import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart';

abstract class NotificationRepository {
  Future<Result<List<Notification>>> list({int page = 1, int limit = 20});
  Future<Result<void>> markRead(String id);
  Future<Result<void>> markAllRead();
  Future<Result<AppSettings>> getSettings();
  Future<Result<void>> updateSettings(AppSettings settings);
}
