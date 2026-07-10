import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/repositories/quick_action_repository.dart';

class ExecuteQuickActionUseCase {
  final QuickActionRepository _quickActionRepository;

  ExecuteQuickActionUseCase(this._quickActionRepository);

  Future<Result<void>> call(String id) {
    return _quickActionRepository.execute(id);
  }
}
