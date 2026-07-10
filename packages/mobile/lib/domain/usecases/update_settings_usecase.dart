import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/repositories/settings_repository.dart';

class UpdateSettingsUseCase {
  final SettingsRepository _settingsRepository;

  UpdateSettingsUseCase(this._settingsRepository);

  Future<Result<void>> call(AppSettings settings) {
    return _settingsRepository.update(settings);
  }
}
