import 'package:equatable/equatable.dart';

class SyncStatus extends Equatable {
  final bool isSyncing;
  final DateTime? lastSyncedAt;
  final int pendingItems;
  final int failedItems;

  const SyncStatus({
    required this.isSyncing,
    this.lastSyncedAt,
    required this.pendingItems,
    required this.failedItems,
  });

  @override
  List<Object?> get props => [
        isSyncing,
        lastSyncedAt,
        pendingItems,
        failedItems,
      ];
}
