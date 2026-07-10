import 'package:jarvis_mobile/domain/entities/session.dart';

class SessionModel {
  final String id;
  final String token;
  final String refreshToken;
  final DateTime expiresAt;
  final String? workspaceId;

  const SessionModel({
    required this.id,
    required this.token,
    required this.refreshToken,
    required this.expiresAt,
    this.workspaceId,
  });

  factory SessionModel.fromJson(Map<String, dynamic> json) {
    return SessionModel(
      id: json['id'] as String,
      token: json['token'] as String,
      refreshToken: json['refreshToken'] as String,
      expiresAt: DateTime.parse(json['expiresAt'] as String),
      workspaceId: json['workspaceId'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'token': token,
      'refreshToken': refreshToken,
      'expiresAt': expiresAt.toIso8601String(),
      'workspaceId': workspaceId,
    };
  }

  Session toEntity() {
    return Session(
      id: id,
      token: token,
      refreshToken: refreshToken,
      expiresAt: expiresAt,
      workspaceId: workspaceId,
    );
  }

  factory SessionModel.fromEntity(Session entity) {
    return SessionModel(
      id: entity.id,
      token: entity.token,
      refreshToken: entity.refreshToken,
      expiresAt: entity.expiresAt,
      workspaceId: entity.workspaceId,
    );
  }
}
