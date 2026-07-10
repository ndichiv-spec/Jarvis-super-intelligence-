import 'package:equatable/equatable.dart';

enum ThemeModeSetting { system, light, dark }

class AppSettings extends Equatable {
  final ThemeModeSetting themeMode;
  final String locale;
  final bool notificationsEnabled;
  final bool biometricEnabled;
  final bool offlineModeEnabled;
  final String? workspaceId;

  const AppSettings({
    required this.themeMode,
    required this.locale,
    required this.notificationsEnabled,
    required this.biometricEnabled,
    required this.offlineModeEnabled,
    this.workspaceId,
  });

  @override
  List<Object?> get props => [
        themeMode,
        locale,
        notificationsEnabled,
        biometricEnabled,
        offlineModeEnabled,
        workspaceId,
      ];
}
