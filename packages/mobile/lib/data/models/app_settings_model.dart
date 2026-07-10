import 'package:jarvis_mobile/domain/entities/app_settings.dart';

class AppSettingsModel {
  final String themeMode;
  final String locale;
  final bool notificationsEnabled;
  final bool biometricEnabled;
  final bool offlineModeEnabled;
  final String? workspaceId;

  const AppSettingsModel({
    required this.themeMode,
    required this.locale,
    required this.notificationsEnabled,
    required this.biometricEnabled,
    required this.offlineModeEnabled,
    this.workspaceId,
  });

  factory AppSettingsModel.fromJson(Map<String, dynamic> json) {
    return AppSettingsModel(
      themeMode: json['themeMode'] as String,
      locale: json['locale'] as String,
      notificationsEnabled: json['notificationsEnabled'] as bool,
      biometricEnabled: json['biometricEnabled'] as bool,
      offlineModeEnabled: json['offlineModeEnabled'] as bool,
      workspaceId: json['workspaceId'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'themeMode': themeMode,
      'locale': locale,
      'notificationsEnabled': notificationsEnabled,
      'biometricEnabled': biometricEnabled,
      'offlineModeEnabled': offlineModeEnabled,
      'workspaceId': workspaceId,
    };
  }

  AppSettings toEntity() {
    return AppSettings(
      themeMode: ThemeModeSetting.values.firstWhere(
        (e) => e.name == themeMode,
        orElse: () => ThemeModeSetting.system,
      ),
      locale: locale,
      notificationsEnabled: notificationsEnabled,
      biometricEnabled: biometricEnabled,
      offlineModeEnabled: offlineModeEnabled,
      workspaceId: workspaceId,
    );
  }

  factory AppSettingsModel.fromEntity(AppSettings entity) {
    return AppSettingsModel(
      themeMode: entity.themeMode.name,
      locale: entity.locale,
      notificationsEnabled: entity.notificationsEnabled,
      biometricEnabled: entity.biometricEnabled,
      offlineModeEnabled: entity.offlineModeEnabled,
      workspaceId: entity.workspaceId,
    );
  }
}
