import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

class HttpClient {
  HttpClient({required String baseUrl, http.Client? client})
    : _baseUrl = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl,
      _client = client ?? http.Client();

  final String _baseUrl;
  final http.Client _client;
  final Map<String, String> _defaultHeaders = {};
  String? _sessionId;

  String get baseUrl => _baseUrl;

  Map<String, String> get defaultHeaders => Map<String, String>.from(_defaultHeaders);

  void setDefaultHeader(String key, String value) {
    _defaultHeaders[key] = value;
  }

  void setSessionId(String? sessionId) {
    _sessionId = sessionId;
    if (sessionId != null) {
      _defaultHeaders['x-session-id'] = sessionId;
    } else {
      _defaultHeaders.remove('x-session-id');
    }
  }

  String? get sessionId => _sessionId;

  Map<String, String> get _headers => Map<String, String>.from(_defaultHeaders);

  Future<HttpResponse> get(String path, {Map<String, String>? queryParams}) async {
    final uri = _buildUri(path, queryParams);
    try {
      final response = await _client.get(uri, headers: _headers);
      return _processResponse(response);
    } on SocketException catch (e) {
      throw NetworkException('No internet connection: ${e.message}');
    } on HttpException catch (e) {
      throw NetworkException('HTTP error: ${e.message}');
    }
  }

  Future<HttpResponse> post(String path, {Object? body, Map<String, String>? queryParams}) async {
    final uri = _buildUri(path, queryParams);
    try {
      final response = await _client.post(
        uri,
        headers: _headers,
        body: body != null ? jsonEncode(body) : null,
      );
      return _processResponse(response);
    } on SocketException catch (e) {
      throw NetworkException('No internet connection: ${e.message}');
    } on HttpException catch (e) {
      throw NetworkException('HTTP error: ${e.message}');
    }
  }

  Future<HttpResponse> put(String path, {Object? body, Map<String, String>? queryParams}) async {
    final uri = _buildUri(path, queryParams);
    try {
      final response = await _client.put(
        uri,
        headers: _headers,
        body: body != null ? jsonEncode(body) : null,
      );
      return _processResponse(response);
    } on SocketException catch (e) {
      throw NetworkException('No internet connection: ${e.message}');
    } on HttpException catch (e) {
      throw NetworkException('HTTP error: ${e.message}');
    }
  }

  Future<HttpResponse> patch(String path, {Object? body, Map<String, String>? queryParams}) async {
    final uri = _buildUri(path, queryParams);
    try {
      final response = await _client.patch(
        uri,
        headers: _headers,
        body: body != null ? jsonEncode(body) : null,
      );
      return _processResponse(response);
    } on SocketException catch (e) {
      throw NetworkException('No internet connection: ${e.message}');
    } on HttpException catch (e) {
      throw NetworkException('HTTP error: ${e.message}');
    }
  }

  Future<HttpResponse> delete(String path, {Map<String, String>? queryParams}) async {
    final uri = _buildUri(path, queryParams);
    try {
      final response = await _client.delete(uri, headers: _headers);
      return _processResponse(response);
    } on SocketException catch (e) {
      throw NetworkException('No internet connection: ${e.message}');
    } on HttpException catch (e) {
      throw NetworkException('HTTP error: ${e.message}');
    }
  }

  Uri _buildUri(String path, Map<String, String>? queryParams) {
    final uri = Uri.parse('$_baseUrl/gateway$path');
    if (queryParams != null && queryParams.isNotEmpty) {
      return uri.replace(queryParameters: queryParams);
    }
    return uri;
  }

  HttpResponse _processResponse(http.Response response) {
    final statusCode = response.statusCode;
    Map<String, dynamic>? body;

    try {
      if (response.body.isNotEmpty) {
        body = jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {
      body = {'raw': response.body};
    }

    if (statusCode >= 200 && statusCode < 300) {
      return HttpResponse(statusCode: statusCode, body: body);
    }

    if (statusCode == 429) {
      final retryAfter = response.headers['retry-after'];
      throw RateLimitException(
        'Rate limit exceeded',
        retryAfterSeconds: retryAfter != null ? int.tryParse(retryAfter) : null,
      );
    }

    if (statusCode == 401 || statusCode == 403) {
      throw AuthenticationException(
        body?['error']?['message'] as String? ?? 'Authentication failed',
        code: body?['error']?['code'] as String?,
      );
    }

    throw GatewayException.fromResponse(statusCode, body ?? {});
  }

  void dispose() {
    _client.close();
  }
}

class HttpResponse {
  final int statusCode;
  final Map<String, dynamic>? body;

  HttpResponse({required this.statusCode, this.body});

  bool get isOk => body?['ok'] == true;

  T? data<T>(T Function(dynamic json) fromJson) {
    final data = body?['data'];
    if (data == null) return null;
    return fromJson(data);
  }

  T dataOrThrow<T>(T Function(dynamic json) fromJson) {
    final data = body?['data'];
    if (data == null) {
      throw GatewayException('No data in response', code: 'NO_DATA');
    }
    return fromJson(data);
  }

  Map<String, dynamic>? get metadata => body?['metadata'] as Map<String, dynamic>?;
  Map<String, dynamic>? get error => body?['error'] as Map<String, dynamic>?;
}
