import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/device.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/device.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/repositories/security_repository.dart';
import 'package:jarvis_mobile/domain/usecases/manage_sessions_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class SecurityState {
  final List<Session> sessions;
  final List<Device> devices;
  final bool isLoading;

  const SecurityState({
    this.sessions = const [],
    this.devices = const [],
    this.isLoading = false,
  });

  SecurityState copyWith({
    List<Session>? sessions,
    List<Device>? devices,
    bool? isLoading,
  }) {
    return SecurityState(
      sessions: sessions ?? this.sessions,
      devices: devices ?? this.devices,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class SecurityNotifier extends StateNotifier<SecurityState> {
  final ManageSessionsUseCase _useCase;
  final SecurityRepository _repository;

  SecurityNotifier({
    required ManageSessionsUseCase useCase,
    required SecurityRepository repository,
  })  : _useCase = useCase,
        _repository = repository,
        super(const SecurityState());

  Future<void> loadAll() async {
    state = state.copyWith(isLoading: true);
    try {
      final results = await Future.wait([
        _useCase.listSessions(),
        _useCase.listDevices(),
      ]);
      final sessionsResult = results[0];
      final devicesResult = results[1];
      if (sessionsResult is Success<List<Session>>) {
        state = state.copyWith(sessions: sessionsResult.data);
      }
      if (devicesResult is Success<List<Device>>) {
        state = state.copyWith(devices: devicesResult.data);
      }
      state = state.copyWith(isLoading: false);
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> listSessions() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _useCase.listSessions();
      switch (result) {
        case Success<List<Session>>():
          state = state.copyWith(sessions: result.data, isLoading: false);
        case Failure<List<Session>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> revokeSession(String id) async {
    try {
      final result = await _useCase.revokeSession(id);
      if (result is Success<void>) {
        state = state.copyWith(
          sessions: state.sessions.where((s) => s.id != id).toList(),
        );
      }
    } catch (_) {}
  }

  Future<void> listDevices() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _useCase.listDevices();
      switch (result) {
        case Success<List<Device>>():
          state = state.copyWith(devices: result.data, isLoading: false);
        case Failure<List<Device>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> registerDevice(String name, String type) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.registerDevice(name, type);
      switch (result) {
        case Success<Device>():
          state = state.copyWith(devices: [...state.devices, result.data], isLoading: false);
        case Failure<Device>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> trustDevice(String id) async {
    try {
      final result = await _useCase.trustDevice(id);
      if (result is Success<void>) {
        state = state.copyWith(
          devices: state.devices.map((d) {
            if (d.id == id) {
              return Device(
                id: d.id,
                name: d.name,
                type: d.type,
                platform: d.platform,
                lastSeenAt: d.lastSeenAt,
                isTrusted: true,
                isCurrentDevice: d.isCurrentDevice,
              );
            }
            return d;
          }).toList(),
        );
      }
    } catch (_) {}
  }

  Future<void> removeDevice(String id) async {
    try {
      final result = await _useCase.removeDevice(id);
      if (result is Success<void>) {
        state = state.copyWith(
          devices: state.devices.where((d) => d.id != id).toList(),
        );
      }
    } catch (_) {}
  }
}

final securityProvider = StateNotifierProvider<SecurityNotifier, SecurityState>((ref) {
  return SecurityNotifier(
    useCase: ref.watch(manageSessionsUseCaseProvider),
    repository: ref.watch(securityRepositoryProvider),
  );
});
