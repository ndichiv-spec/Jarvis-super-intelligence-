import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart';
import 'package:jarvis_mobile/domain/repositories/notification_repository.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class NotificationState {
  final List<Notification> notifications;
  final int unreadCount;
  final bool isLoading;

  const NotificationState({
    this.notifications = const [],
    this.unreadCount = 0,
    this.isLoading = false,
  });

  int get _computeUnread => notifications.where((n) => !n.isRead).length;

  NotificationState copyWith({
    List<Notification>? notifications,
    int? unreadCount,
    bool? isLoading,
  }) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this._computeUnread,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class NotificationNotifier extends StateNotifier<NotificationState> {
  final NotificationRepository _repository;

  NotificationNotifier(this._repository) : super(const NotificationState());

  Future<void> list() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.list();
      switch (result) {
        case Success<List<Notification>>():
          state = state.copyWith(notifications: result.data, isLoading: false);
        case Failure<List<Notification>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> markRead(String id) async {
    try {
      final result = await _repository.markRead(id);
      if (result is Success<void>) {
        state = state.copyWith(
          notifications: state.notifications.map((n) {
            if (n.id == id) {
              return Notification(
                id: n.id,
                type: n.type,
                title: n.title,
                body: n.body,
                isRead: true,
                createdAt: n.createdAt,
                actionPayload: n.actionPayload,
              );
            }
            return n;
          }).toList(),
        );
      }
    } catch (_) {}
  }

  Future<void> markAllRead() async {
    try {
      final result = await _repository.markAllRead();
      if (result is Success<void>) {
        state = state.copyWith(
          notifications: state.notifications.map((n) {
            return Notification(
              id: n.id,
              type: n.type,
              title: n.title,
              body: n.body,
              isRead: true,
              createdAt: n.createdAt,
              actionPayload: n.actionPayload,
            );
          }).toList(),
        );
      }
    } catch (_) {}
  }
}

final notificationProvider =
    StateNotifierProvider<NotificationNotifier, NotificationState>((ref) {
  return NotificationNotifier(ref.watch(notificationRepositoryProvider));
});
