import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/device.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/repositories/security_repository.dart';

class ManageSessionsUseCase {
  final SecurityRepository _securityRepository;

  ManageSessionsUseCase(this._securityRepository);

  Future<Result<List<Session>>> listSessions() {
    return _securityRepository.listSessions();
  }

  Future<Result<void>> revokeSession(String id) {
    return _securityRepository.revokeSession(id);
  }

  Future<Result<List<Device>>> listDevices() {
    return _securityRepository.listDevices();
  }

  Future<Result<void>> trustDevice(String id) {
    return _securityRepository.trustDevice(id);
  }

  Future<Result<void>> removeDevice(String id) {
    return _securityRepository.removeDevice(id);
  }
}
