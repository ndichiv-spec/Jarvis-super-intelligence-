import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

class SseClient {
  SseClient({required this.baseUrl});

  final String baseUrl;

  Stream<Map<String, dynamic>> stream(String path, {Map<String, String>? headers}) {
    final uri = Uri.parse('$baseUrl/gateway/stream$path');
    final request = http.Request('GET', uri);
    headers?.forEach((key, value) {
      request.headers[key] = value;
    });

    return _sseStream(request);
  }

  Stream<Map<String, dynamic>> _sseStream(http.Request request) {
    final controller = StreamController<Map<String, dynamic>>();

    http.Client().send(request).then((response) {
      final stream = response.stream;
      String buffer = '';
      stream.transform(utf8.decoder).listen(
        (data) {
          buffer += data;
          final lines = buffer.split('\n');
          buffer = lines.removeLast();

          for (final line in lines) {
            if (line.startsWith('data: ')) {
              final jsonStr = line.substring(6);
              try {
                final decoded = jsonDecode(jsonStr) as Map<String, dynamic>;
                controller.add(decoded);
              } catch (_) {
                // Skip malformed SSE data
              }
            }
          }
        },
        onError: (error) => controller.addError(error),
        onDone: () => controller.close(),
      );
    }).catchError((error) {
      controller.addError(error);
    });

    return controller.stream;
  }
}
