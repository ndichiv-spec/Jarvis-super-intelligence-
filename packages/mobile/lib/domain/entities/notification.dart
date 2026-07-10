import 'package:equatable/equatable.dart';

class Notification extends Equatable {
  final String id;
  final String type;
  final String title;
  final String body;
  final bool isRead;
  final DateTime createdAt;
  final Map<String, dynamic>? actionPayload;

  const Notification({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.isRead,
    required this.createdAt,
    this.actionPayload,
  });

  @override
  List<Object?> get props => [
        id,
        type,
        title,
        body,
        isRead,
        createdAt,
        actionPayload,
      ];
}
