import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart';
import 'package:jarvis_mobile/domain/repositories/notification_repository.dart';

class GetNotificationsUseCase {
  final NotificationRepository _notificationRepository;

  GetNotificationsUseCase(this._notificationRepository);

  Future<Result<List<Notification>>> call({int page = 1, int limit = 20}) {
    return _notificationRepository.list(page: page, limit: limit);
  }
}
