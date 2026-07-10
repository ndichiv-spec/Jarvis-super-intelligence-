import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';

abstract class SettingsRepository {
  Future<Result<AppSettings>> get();
  Future<Result<void>> update(AppSettings settings);
}
