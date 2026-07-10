import 'dart:async';
import 'dart:convert';

import 'package:uuid/uuid.dart';

import 'local_database.dart';
import 'connectivity_service.dart';

class OfflineAction {
  final String id;
  final String actionType;
  final Map<String, dynamic> payload;
  final DateTime createdAt;
  final String status;

  OfflineAction({
    required this.id,
    required this.actionType,
    required this.payload,
    required this.createdAt,
    this.status = 'pending',
  });
}

class OfflineQueue {
  OfflineQueue({
    required LocalDatabase database,
    required ConnectivityService connectivityService,
  }) : _database = database,
       _connectivityService = connectivityService;

  final LocalDatabase _database;
  final ConnectivityService _connectivityService;
  final _uuid = const Uuid();
  StreamSubscription<bool>? _connectivitySubscription;
  final List<OfflineAction> _failedActions = [];

  int get pendingCount => _pendingCount;
  int _pendingCount = 0;
  List<OfflineAction> get failedActions => List.unmodifiable(_failedActions);

  final StreamController<int> _pendingController = StreamController<int>.broadcast();
  Stream<int> get onPendingCountChanged => _pendingController.stream;

  Future<void> initialize() async {
    await _loadPendingCount();
    _connectivitySubscription = _connectivityService.onConnectivityChanged.listen((connected) {
      if (connected) processQueue();
    });
  }

  Future<void> _loadPendingCount() async {
    final rows = await _database.query('offline_actions', where: 'status = ?', whereArgs: ['pending']);
    _pendingCount = rows.length;
    _pendingController.add(_pendingCount);
  }

  Future<void> enqueue(String actionType, Map<String, dynamic> payload) async {
    final action = {
      'id': _uuid.v4(),
      'action_type': actionType,
      'payload': jsonEncode(payload),
      'created_at': DateTime.now().toIso8601String(),
      'status': 'pending',
    };
    await _database.insert('offline_actions', action);
    _pendingCount++;
    _pendingController.add(_pendingCount);
  }

  Future<void> processQueue() async {
    final rows = await _database.query('offline_actions',
        where: 'status = ?', whereArgs: ['pending'], orderBy: 'created_at ASC');
    for (final row in rows) {
      try {
        await _processAction(row);
        await _database.update('offline_actions', {'status': 'completed'},
            where: 'id = ?', whereArgs: [row['id']]);
        _pendingCount--;
        _pendingController.add(_pendingCount);
      } catch (e) {
        await _database.update('offline_actions', {'status': 'failed'},
            where: 'id = ?', whereArgs: [row['id']]);
        _pendingCount--;
        _pendingController.add(_pendingCount);
        _failedActions.add(OfflineAction(
          id: row['id'] as String,
          actionType: row['action_type'] as String,
          payload: jsonDecode(row['payload'] as String) as Map<String, dynamic>,
          createdAt: DateTime.parse(row['created_at'] as String),
          status: 'failed',
        ));
      }
    }
  }

  Future<void> _processAction(Map<String, dynamic> row) async {
    // Override in subclass or inject processor
  }

  Future<void> clearFailed() async {
    await _database.delete('offline_actions', where: 'status = ?', whereArgs: ['failed']);
    _failedActions.clear();
  }

  Future<int> getPendingCount() async {
    final rows = await _database.query('offline_actions', where: 'status = ?', whereArgs: ['pending']);
    return rows.length;
  }

  void dispose() {
    _connectivitySubscription?.cancel();
    _pendingController.close();
  }
}
