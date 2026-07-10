import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/repositories/auth_repository.dart';

class LogoutUseCase {
  final AuthRepository _authRepository;

  LogoutUseCase(this._authRepository);

  Future<Result<void>> call() {
    return _authRepository.logout();
  }
}
