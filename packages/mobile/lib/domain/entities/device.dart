import 'package:equatable/equatable.dart';

class Device extends Equatable {
  final String id;
  final String name;
  final String type;
  final String platform;
  final DateTime lastSeenAt;
  final bool isTrusted;
  final bool isCurrentDevice;

  const Device({
    required this.id,
    required this.name,
    required this.type,
    required this.platform,
    required this.lastSeenAt,
    required this.isTrusted,
    required this.isCurrentDevice,
  });

  @override
  List<Object?> get props => [
        id,
        name,
        type,
        platform,
        lastSeenAt,
        isTrusted,
        isCurrentDevice,
      ];
}
