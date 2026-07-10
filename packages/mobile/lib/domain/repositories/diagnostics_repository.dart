import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_health.dart';
import 'package:jarvis_mobile/domain/entities/sync_status.dart';

abstract class DiagnosticsRepository {
  Future<Result<AppHealth>> getHealth();
  Future<Result<Map<String, bool>>> getConnectivityStatus();
  Future<Result<SyncStatus>> getSyncStatus();
  Future<Result<List<Map<String, dynamic>>>> getOfflineQueue();
}
