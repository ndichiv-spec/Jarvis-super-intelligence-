import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class ConnectivityService {
  ConnectivityService() : _connectivity = Connectivity();

  final Connectivity _connectivity;
  StreamSubscription<List<ConnectivityResult>>? _subscription;
  bool _isConnected = true;

  bool get isConnected => _isConnected;

  final StreamController<bool> _controller = StreamController<bool>.broadcast();
  Stream<bool> get onConnectivityChanged => _controller.stream;

  Future<void> initialize() async {
    final result = await _connectivity.checkConnectivity();
    _isConnected = result.any((r) => r != ConnectivityResult.none);
    _subscription = _connectivity.onConnectivityChanged.listen(_updateConnectionStatus);
  }

  void _updateConnectionStatus(List<ConnectivityResult> results) {
    final connected = results.any((r) => r != ConnectivityResult.none);
    if (connected != _isConnected) {
      _isConnected = connected;
      _controller.add(connected);
    }
  }

  Future<bool> checkConnectivity() async {
    final result = await _connectivity.checkConnectivity();
    _isConnected = result.any((r) => r != ConnectivityResult.none);
    return _isConnected;
  }

  void dispose() {
    _subscription?.cancel();
    _controller.close();
  }
}
