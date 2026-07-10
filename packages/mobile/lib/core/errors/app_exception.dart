sealed class AppException implements Exception {
  const AppException(this.message, {this.code, this.details});

  final String message;
  final String? code;
  final Map<String, dynamic>? details;
}

class NetworkException extends AppException {
  const NetworkException(super.message, {super.code, super.details});
}

class AuthenticationException extends AppException {
  const AuthenticationException(super.message, {super.code, super.details});
}

class GatewayException extends AppException {
  const GatewayException(super.message, {super.code, super.details});

  factory GatewayException.fromResponse(
    int statusCode,
    Map<String, dynamic> body,
  ) {
    final error = body['error'] as Map<String, dynamic>?;
    return GatewayException(
      error?['message'] as String? ?? 'Gateway error',
      code: error?['code'] as String? ?? 'ERROR_$statusCode',
      details: error?['details'] as Map<String, dynamic>?,
    );
  }
}

class CacheException extends AppException {
  const CacheException(super.message, {super.code, super.details});
}

class ValidationException extends AppException {
  const ValidationException(super.message, {super.code, super.details});
}

class OfflineException extends AppException {
  const OfflineException(super.message, {super.code, super.details});
}

class RateLimitException extends AppException {
  const RateLimitException(super.message, {
    this.retryAfterSeconds,
    super.code,
    super.details,
  });

  final int? retryAfterSeconds;
}

class BiometricException extends AppException {
  const BiometricException(super.message, {super.code, super.details});
}
