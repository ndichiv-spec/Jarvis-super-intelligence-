import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/repositories/settings_repository.dart';

class GetSettingsUseCase {
  final SettingsRepository _settingsRepository;

  GetSettingsUseCase(this._settingsRepository);

  Future<Result<AppSettings>> call() {
    return _settingsRepository.get();
  }
}
