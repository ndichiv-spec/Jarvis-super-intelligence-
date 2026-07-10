import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/core/errors/app_exception.dart';

void main() {
  group('AppException', () {
    test('NetworkException', () {
      final e = NetworkException('no connection');
      expect(e.message, 'no connection');
      expect(e, isA<NetworkException>());
    });

    test('AuthenticationException', () {
      final e = AuthenticationException('invalid token', code: 'TOKEN_EXPIRED');
      expect(e.message, 'invalid token');
      expect(e.code, 'TOKEN_EXPIRED');
    });

    test('GatewayException.fromResponse', () {
      final e = GatewayException.fromResponse(404, {'error': {'code': 'NOT_FOUND', 'message': 'Resource not found'}});
      expect(e.statusCode, 404);
      expect(e.message, 'Resource not found');
      expect(e.code, 'NOT_FOUND');
    });

    test('GatewayException default message', () {
      final e = GatewayException.fromResponse(500, {});
      expect(e.message, 'Unknown error');
      expect(e.statusCode, 500);
    });

    test('RateLimitException', () {
      final e = RateLimitException('too fast', retryAfterSeconds: 30);
      expect(e.message, 'too fast');
      expect(e.retryAfterSeconds, 30);
    });

    test('OfflineException', () {
      final e = OfflineException('no network');
      expect(e.message, 'no network');
    });

    test('CacheException', () {
      final e = CacheException('cache miss');
      expect(e.message, 'cache miss');
    });

    test('ValidationException', () {
      final e = ValidationException('invalid input');
      expect(e.message, 'invalid input');
    });

    test('BiometricException', () {
      final e = BiometricException('biometric failed');
      expect(e.message, 'biometric failed');
    });
  });
}
