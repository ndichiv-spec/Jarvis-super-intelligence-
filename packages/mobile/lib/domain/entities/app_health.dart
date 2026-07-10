import 'package:equatable/equatable.dart';

enum HealthStatus { healthy, degraded, error }

class AppHealth extends Equatable {
  final HealthStatus status;
  final bool gatewayConnected;
  final DateTime lastCheckedAt;
  final String version;

  const AppHealth({
    required this.status,
    required this.gatewayConnected,
    required this.lastCheckedAt,
    required this.version,
  });

  @override
  List<Object?> get props => [
        status,
        gatewayConnected,
        lastCheckedAt,
        version,
      ];
}
