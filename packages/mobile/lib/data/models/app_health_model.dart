import 'package:jarvis_mobile/domain/entities/app_health.dart';

class AppHealthModel {
  final String status;
  final bool gatewayConnected;
  final DateTime lastCheckedAt;
  final String version;

  const AppHealthModel({
    required this.status,
    required this.gatewayConnected,
    required this.lastCheckedAt,
    required this.version,
  });

  factory AppHealthModel.fromJson(Map<String, dynamic> json) {
    return AppHealthModel(
      status: json['status'] as String,
      gatewayConnected: json['gatewayConnected'] as bool,
      lastCheckedAt: DateTime.parse(json['lastCheckedAt'] as String),
      version: json['version'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'status': status,
      'gatewayConnected': gatewayConnected,
      'lastCheckedAt': lastCheckedAt.toIso8601String(),
      'version': version,
    };
  }

  AppHealth toEntity() {
    return AppHealth(
      status: HealthStatus.values.firstWhere(
        (e) => e.name == status,
        orElse: () => HealthStatus.healthy,
      ),
      gatewayConnected: gatewayConnected,
      lastCheckedAt: lastCheckedAt,
      version: version,
    );
  }

  factory AppHealthModel.fromEntity(AppHealth entity) {
    return AppHealthModel(
      status: entity.status.name,
      gatewayConnected: entity.gatewayConnected,
      lastCheckedAt: entity.lastCheckedAt,
      version: entity.version,
    );
  }
}
