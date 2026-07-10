import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/device.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';

abstract class SecurityRepository {
  Future<Result<List<Session>>> listSessions();
  Future<Result<void>> revokeSession(String id);
  Future<Result<List<Device>>> listDevices();
  Future<Result<Device>> registerDevice(String name, String type);
  Future<Result<void>> trustDevice(String id);
  Future<Result<void>> removeDevice(String id);
}
