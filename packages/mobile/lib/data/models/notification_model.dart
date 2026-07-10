import 'package:jarvis_mobile/domain/entities/notification.dart' as domain;

class NotificationModel {
  final String id;
  final String type;
  final String title;
  final String body;
  final bool isRead;
  final DateTime createdAt;
  final Map<String, dynamic>? actionPayload;

  const NotificationModel({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.isRead,
    required this.createdAt,
    this.actionPayload,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      isRead: json['isRead'] as bool,
      createdAt: DateTime.parse(json['createdAt'] as String),
      actionPayload: json['actionPayload'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'body': body,
      'isRead': isRead,
      'createdAt': createdAt.toIso8601String(),
      'actionPayload': actionPayload,
    };
  }

  domain.Notification toEntity() {
    return domain.Notification(
      id: id,
      type: type,
      title: title,
      body: body,
      isRead: isRead,
      createdAt: createdAt,
      actionPayload: actionPayload,
    );
  }

  factory NotificationModel.fromEntity(domain.Notification entity) {
    return NotificationModel(
      id: entity.id,
      type: entity.type,
      title: entity.title,
      body: entity.body,
      isRead: entity.isRead,
      createdAt: entity.createdAt,
      actionPayload: entity.actionPayload,
    );
  }
}
