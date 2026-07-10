import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/network/connectivity_service.dart';
import 'package:jarvis_mobile/core/network/local_database.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/diagnostics_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/app_health.dart';
import 'package:jarvis_mobile/domain/entities/sync_status.dart';
import 'package:jarvis_mobile/domain/repositories/diagnostics_repository.dart';

class DiagnosticsRepositoryImpl implements DiagnosticsRepository {
  DiagnosticsRepositoryImpl({
    required this.remoteDataSource,
    required this.connectivityService,
    required this.localDatabase,
  });

  final DiagnosticsRemoteDataSource remoteDataSource;
  final ConnectivityService connectivityService;
  final LocalDatabase localDatabase;

  @override
  Future<Result<AppHealth>> getHealth() async {
    try {
      final model = await remoteDataSource.getHealth();
      return Result.success(model.toEntity());
    } on AppException {
      final connected = await connectivityService.checkConnectivity();
      return Result.success(
        AppHealth(
          status: connected ? HealthStatus.degraded : HealthStatus.error,
          gatewayConnected: connected,
          lastCheckedAt: DateTime.now(),
          version: '1.0.0',
        ),
      );
    }
  }

  @override
  Future<Result<Map<String, bool>>> getConnectivityStatus() async {
    try {
      final connected = await connectivityService.checkConnectivity();
      return Result.success({
        'gateway': connected,
        'websocket': connected,
        'offline_queue': !connected,
      });
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<SyncStatus>> getSyncStatus() async {
    try {
      final pendingRows = await localDatabase.query(
        'offline_actions',
        where: 'status = ?',
        whereArgs: ['pending'],
      );
      final failedRows = await localDatabase.query(
        'offline_actions',
        where: 'status = ?',
        whereArgs: ['failed'],
      );
      return Result.success(
        SyncStatus(
          isSyncing: pendingRows.isNotEmpty,
          lastSyncedAt: DateTime.now(),
          pendingItems: pendingRows.length,
          failedItems: failedRows.length,
        ),
      );
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<Map<String, dynamic>>>> getOfflineQueue() async {
    try {
      final rows = await localDatabase.query(
        'offline_actions',
        orderBy: 'created_at ASC',
      );
      return Result.success(rows);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
