import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/network/connectivity_service.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_health.dart';
import 'package:jarvis_mobile/domain/entities/sync_status.dart';
import 'package:jarvis_mobile/domain/usecases/get_diagnostics_usecase.dart';
import 'package:jarvis_mobile/domain/repositories/diagnostics_repository.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class DiagnosticsState {
  final AppHealth? health;
  final Map<String, bool> connectivityInfo;
  final SyncStatus? syncStatus;
  final List<Map<String, dynamic>> offlineQueue;
  final bool isLoading;

  const DiagnosticsState({
    this.health,
    this.connectivityInfo = const {},
    this.syncStatus,
    this.offlineQueue = const [],
    this.isLoading = false,
  });

  DiagnosticsState copyWith({
    AppHealth? health,
    Map<String, bool>? connectivityInfo,
    SyncStatus? syncStatus,
    List<Map<String, dynamic>>? offlineQueue,
    bool? isLoading,
  }) {
    return DiagnosticsState(
      health: health ?? this.health,
      connectivityInfo: connectivityInfo ?? this.connectivityInfo,
      syncStatus: syncStatus ?? this.syncStatus,
      offlineQueue: offlineQueue ?? this.offlineQueue,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class DiagnosticsNotifier extends StateNotifier<DiagnosticsState> {
  final GetDiagnosticsUseCase _getDiagnosticsUseCase;
  final DiagnosticsRepository _repository;
  final ConnectivityService _connectivityService;

  DiagnosticsNotifier({
    required GetDiagnosticsUseCase getDiagnosticsUseCase,
    required DiagnosticsRepository repository,
    required ConnectivityService connectivityService,
  })  : _getDiagnosticsUseCase = getDiagnosticsUseCase,
        _repository = repository,
        _connectivityService = connectivityService,
        super(const DiagnosticsState());

  Future<void> loadAll() async {
    state = state.copyWith(isLoading: true);
    try {
      final connectivityInfo = await _connectivityService.checkConnectivity();
      final infoResult = await _getDiagnosticsUseCase.call();
      switch (infoResult) {
        case Success<ConnectivityInfo>():
          state = state.copyWith(
            health: infoResult.data.health,
            connectivityInfo: infoResult.data.connectivity,
            syncStatus: infoResult.data.syncStatus,
            isLoading: false,
          );
        case Failure<ConnectivityInfo>():
          state = state.copyWith(isLoading: false);
      }
      try {
        final queueResult = await _repository.getOfflineQueue();
        if (queueResult is Success<List<Map<String, dynamic>>>) {
          state = state.copyWith(offlineQueue: queueResult.data);
        }
      } catch (_) {}
      state = state.copyWith(
        connectivityInfo: {...state.connectivityInfo, 'device': connectivityInfo},
      );
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }
}

final diagnosticsProvider =
    StateNotifierProvider<DiagnosticsNotifier, DiagnosticsState>((ref) {
  return DiagnosticsNotifier(
    getDiagnosticsUseCase: ref.watch(getDiagnosticsUseCaseProvider),
    repository: ref.watch(diagnosticsRepositoryProvider),
    connectivityService: ref.watch(connectivityServiceProvider),
  );
});
