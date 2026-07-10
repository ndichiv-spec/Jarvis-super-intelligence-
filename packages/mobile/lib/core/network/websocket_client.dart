import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketClient {
  WebSocketClient({required this.baseUrl});

  final String baseUrl;
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  bool _isConnected = false;

  bool get isConnected => _isConnected;

  Future<void> connect(
    String path, {
    Map<String, String>? headers,
    void Function(Map<String, dynamic> data)? onMessage,
    void Function(String? error)? onError,
    void Function()? onDone,
  }) async {
    final wsUrl = baseUrl.replaceFirst('https://', 'wss://').replaceFirst('http://', 'ws://');
    final uri = Uri.parse('$wsUrl/gateway/ws$path');

    try {
      _channel = WebSocketChannel.connect(uri);
      _isConnected = true;

      _subscription = _channel!.stream.listen(
        (data) {
          if (data is String) {
            try {
              final decoded = jsonDecode(data) as Map<String, dynamic>;
              onMessage?.call(decoded);
            } catch (_) {
              onMessage?.call({'raw': data});
            }
          } else if (data is Map) {
            onMessage?.call(Map<String, dynamic>.from(data));
          }
        },
        onError: (error) {
          _isConnected = false;
          onError?.call(error.toString());
        },
        onDone: () {
          _isConnected = false;
          onDone?.call();
        },
        cancelOnError: false,
      );
    } on SocketException catch (e) {
      _isConnected = false;
      onError?.call('Connection failed: ${e.message}');
    }
  }

  void send(Map<String, dynamic> data) {
    if (_channel != null && _isConnected) {
      _channel!.sink.add(jsonEncode(data));
    }
  }

  Future<void> disconnect() async {
    await _subscription?.cancel();
    await _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }
}
