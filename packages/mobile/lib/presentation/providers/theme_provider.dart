import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/constants/app_constants.dart';
import 'package:jarvis_mobile/core/security/secure_storage.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

class ThemeNotifier extends StateNotifier<ThemeMode> {
  final SecureStorage _secureStorage;

  ThemeNotifier(this._secureStorage) : super(ThemeMode.system);

  Future<void> loadPreference() async {
    try {
      final value = await _secureStorage.read(AppConstants.prefTheme);
      if (value != null) {
        state = _themeModeFromString(value);
      }
    } catch (_) {}
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    state = mode;
    try {
      await _secureStorage.save(AppConstants.prefTheme, _themeModeToString(mode));
    } catch (_) {}
  }

  Future<void> toggle() async {
    final next = switch (state) {
      ThemeMode.system => ThemeMode.light,
      ThemeMode.light => ThemeMode.dark,
      ThemeMode.dark => ThemeMode.system,
    };
    await setThemeMode(next);
  }

  String _themeModeToString(ThemeMode mode) {
    return switch (mode) {
      ThemeMode.system => 'system',
      ThemeMode.light => 'light',
      ThemeMode.dark => 'dark',
    };
  }

  ThemeMode _themeModeFromString(String value) {
    return switch (value) {
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      _ => ThemeMode.system,
    };
  }
}

final themeProvider = StateNotifierProvider<ThemeNotifier, ThemeMode>((ref) {
  return ThemeNotifier(ref.watch(secureStorageProvider));
});
