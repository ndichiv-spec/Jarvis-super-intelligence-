import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_health.dart';
import 'package:jarvis_mobile/domain/entities/sync_status.dart';
import 'package:jarvis_mobile/domain/repositories/diagnostics_repository.dart';

class ConnectivityInfo {
  final AppHealth health;
  final Map<String, bool> connectivity;
  final SyncStatus syncStatus;

  const ConnectivityInfo({
    required this.health,
    required this.connectivity,
    required this.syncStatus,
  });
}

class GetDiagnosticsUseCase {
  final DiagnosticsRepository _diagnosticsRepository;

  GetDiagnosticsUseCase(this._diagnosticsRepository);

  Future<Result<ConnectivityInfo>> call() async {
    final results = await Future.wait([
      _diagnosticsRepository.getHealth(),
      _diagnosticsRepository.getConnectivityStatus(),
      _diagnosticsRepository.getSyncStatus(),
    ]);

    final health = (results[0] as Success<AppHealth>).data;
    final connectivity = (results[1] as Success<Map<String, bool>>).data;
    final syncStatus = (results[2] as Success<SyncStatus>).data;

    return Result.success(ConnectivityInfo(
      health: health,
      connectivity: connectivity,
      syncStatus: syncStatus,
    ));
  }
}
