import 'package:equatable/equatable.dart';

class Session extends Equatable {
  final String id;
  final String token;
  final String refreshToken;
  final DateTime expiresAt;
  final String? workspaceId;

  const Session({
    required this.id,
    required this.token,
    required this.refreshToken,
    required this.expiresAt,
    this.workspaceId,
  });

  @override
  List<Object?> get props => [id, token, refreshToken, expiresAt, workspaceId];
}
