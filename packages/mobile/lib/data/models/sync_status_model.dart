import 'package:jarvis_mobile/domain/entities/sync_status.dart';

class SyncStatusModel {
  final bool isSyncing;
  final DateTime? lastSyncedAt;
  final int pendingItems;
  final int failedItems;

  const SyncStatusModel({
    required this.isSyncing,
    this.lastSyncedAt,
    required this.pendingItems,
    required this.failedItems,
  });

  factory SyncStatusModel.fromJson(Map<String, dynamic> json) {
    return SyncStatusModel(
      isSyncing: json['isSyncing'] as bool,
      lastSyncedAt: json['lastSyncedAt'] != null ? DateTime.parse(json['lastSyncedAt'] as String) : null,
      pendingItems: json['pendingItems'] as int,
      failedItems: json['failedItems'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'isSyncing': isSyncing,
      'lastSyncedAt': lastSyncedAt?.toIso8601String(),
      'pendingItems': pendingItems,
      'failedItems': failedItems,
    };
  }

  SyncStatus toEntity() {
    return SyncStatus(
      isSyncing: isSyncing,
      lastSyncedAt: lastSyncedAt,
      pendingItems: pendingItems,
      failedItems: failedItems,
    );
  }

  factory SyncStatusModel.fromEntity(SyncStatus entity) {
    return SyncStatusModel(
      isSyncing: entity.isSyncing,
      lastSyncedAt: entity.lastSyncedAt,
      pendingItems: entity.pendingItems,
      failedItems: entity.failedItems,
    );
  }
}
