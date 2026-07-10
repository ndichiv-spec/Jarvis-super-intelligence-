import 'package:jarvis_mobile/domain/entities/device.dart';

class DeviceModel {
  final String id;
  final String name;
  final String type;
  final String platform;
  final DateTime lastSeenAt;
  final bool isTrusted;
  final bool isCurrentDevice;

  const DeviceModel({
    required this.id,
    required this.name,
    required this.type,
    required this.platform,
    required this.lastSeenAt,
    required this.isTrusted,
    required this.isCurrentDevice,
  });

  factory DeviceModel.fromJson(Map<String, dynamic> json) {
    return DeviceModel(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      platform: json['platform'] as String,
      lastSeenAt: DateTime.parse(json['lastSeenAt'] as String),
      isTrusted: json['isTrusted'] as bool,
      isCurrentDevice: json['isCurrentDevice'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'platform': platform,
      'lastSeenAt': lastSeenAt.toIso8601String(),
      'isTrusted': isTrusted,
      'isCurrentDevice': isCurrentDevice,
    };
  }

  Device toEntity() {
    return Device(
      id: id,
      name: name,
      type: type,
      platform: platform,
      lastSeenAt: lastSeenAt,
      isTrusted: isTrusted,
      isCurrentDevice: isCurrentDevice,
    );
  }

  factory DeviceModel.fromEntity(Device entity) {
    return DeviceModel(
      id: entity.id,
      name: entity.name,
      type: entity.type,
      platform: entity.platform,
      lastSeenAt: entity.lastSeenAt,
      isTrusted: entity.isTrusted,
      isCurrentDevice: entity.isCurrentDevice,
    );
  }
}
