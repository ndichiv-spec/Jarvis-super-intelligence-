import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/usecases/get_settings_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/update_settings_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class SettingsState {
  final AppSettings? settings;
  final bool isLoading;

  const SettingsState({
    this.settings,
    this.isLoading = false,
  });

  SettingsState copyWith({
    AppSettings? settings,
    bool? isLoading,
  }) {
    return SettingsState(
      settings: settings ?? this.settings,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class SettingsNotifier extends StateNotifier<SettingsState> {
  final GetSettingsUseCase _getSettingsUseCase;
  final UpdateSettingsUseCase _updateSettingsUseCase;

  SettingsNotifier({
    required GetSettingsUseCase getSettingsUseCase,
    required UpdateSettingsUseCase updateSettingsUseCase,
  })  : _getSettingsUseCase = getSettingsUseCase,
        _updateSettingsUseCase = updateSettingsUseCase,
        super(const SettingsState());

  Future<void> load() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _getSettingsUseCase.call();
      switch (result) {
        case Success<AppSettings>():
          state = state.copyWith(settings: result.data, isLoading: false);
        case Failure<AppSettings>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> update(AppSettings settings) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _updateSettingsUseCase.call(settings);
      switch (result) {
        case Success<void>():
          state = state.copyWith(settings: settings, isLoading: false);
        case Failure<void>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> updateSetting(String key, dynamic value) async {
    final current = state.settings ?? const AppSettings(
      themeMode: ThemeModeSetting.system,
      locale: 'en',
      notificationsEnabled: true,
      biometricEnabled: false,
      offlineModeEnabled: false,
    );
    final updated = switch (key) {
      'biometricEnabled' => AppSettings(
        themeMode: current.themeMode,
        locale: current.locale,
        notificationsEnabled: current.notificationsEnabled,
        biometricEnabled: value as bool,
        offlineModeEnabled: current.offlineModeEnabled,
        workspaceId: current.workspaceId,
      ),
      'notificationsEnabled' => AppSettings(
        themeMode: current.themeMode,
        locale: current.locale,
        notificationsEnabled: value as bool,
        biometricEnabled: current.biometricEnabled,
        offlineModeEnabled: current.offlineModeEnabled,
        workspaceId: current.workspaceId,
      ),
      'offlineModeEnabled' => AppSettings(
        themeMode: current.themeMode,
        locale: current.locale,
        notificationsEnabled: current.notificationsEnabled,
        biometricEnabled: current.biometricEnabled,
        offlineModeEnabled: value as bool,
        workspaceId: current.workspaceId,
      ),
      _ => current,
    };
    await update(updated);
  }
}

final settingsProvider =
    StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  return SettingsNotifier(
    getSettingsUseCase: ref.watch(getSettingsUseCaseProvider),
    updateSettingsUseCase: ref.watch(updateSettingsUseCaseProvider),
  );
});
