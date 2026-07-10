import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/core/constants/api_constants.dart';
import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/constants/app_constants.dart';
import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/core/utils/formatters.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';

void main() {
  group('API Constants', () {
    test('defaultBaseUrl is valid', () {
      expect(ApiConstants.defaultBaseUrl, isNotEmpty);
      expect(ApiConstants.defaultBaseUrl.startsWith('https://'), isTrue);
    });

    test('API version is set', () {
      expect(ApiConstants.apiVersion, isNotEmpty);
    });

    test('subsystem identifiers are defined', () {
      expect(ApiConstants.subsystemBrain, 'brain');
      expect(ApiConstants.subsystemMemory, 'memory');
      expect(ApiConstants.subsystemKnowledge, 'knowledge');
    });
  });

  group('GatewayPaths', () {
    test('auth paths are defined', () {
      expect(GatewayPaths.authLogin, '/auth/login');
      expect(GatewayPaths.authLogout, '/auth/logout');
      expect(GatewayPaths.authRefresh, '/auth/refresh');
      expect(GatewayPaths.authBiometric, '/auth/biometric');
    });

    test('conversation paths are defined', () {
      expect(GatewayPaths.conversationList, '/brain/conversations');
      expect(GatewayPaths.conversationCreate, '/brain/conversations');
      expect(GatewayPaths.conversationStream, '/brain/conversations/stream');
      expect(GatewayPaths.conversationMessages, '/brain/conversations/');
    });

    test('diagnostics paths are defined', () {
      expect(GatewayPaths.diagnosticsHealth, '/health');
      expect(GatewayPaths.diagnosticsStats, '/stats');
    });

    test('quick actions path is defined', () {
      expect(GatewayPaths.quickActions, '/administration/quick-actions');
    });
  });

  group('AppConstants', () {
    test('constants have expected types', () {
      expect(AppConstants.sessionTimeout, 30 * 60 * 1000);
      expect(AppConstants.heartbeatInterval, isPositive);
      expect(AppConstants.reconnectDelay, isPositive);
      expect(AppConstants.defaultPageSize, isPositive);
    });
  });

  group('Result Pattern', () {
    test('Success pattern matching', () {
      final result = Success<String>('data');
      expect(result, isA<Success>());
      switch (result) {
        case Success<String>():
          expect(result.data, 'data');
        case Failure<String>():
          fail('Should not be failure');
      }
    });

    test('Failure pattern matching', () {
      final error = Exception('fail');
      final result = Failure<String>(error);
      expect(result, isA<Failure>());
      switch (result) {
        case Success<String>():
          fail('Should not be success');
        case Failure<String>():
          expect(result.error, error);
      }
    });
  });

  group('Session Entity', () {
    test('creates with required fields', () {
      final session = Session(
        id: 's-1',
        token: 'token',
        refreshToken: 'refresh',
        expiresAt: DateTime(2025, 6, 1),
        workspaceId: 'ws-1',
      );
      expect(session.id, 's-1');
      expect(session.workspaceId, 'ws-1');
    });
  });

  group('Conversation Entity', () {
    test('supports archiving state', () {
      final conv = Conversation(
        id: 'c-1',
        title: 'Test',
        workspaceId: 'ws-1',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        messageCount: 5,
        isArchived: false,
      );
      expect(conv.isArchived, false);
    });
  });

  group('GatewayException', () {
    test('parses error from response', () {
      final response = {
        'error': {
          'code': 'EXECUTION_ERROR',
          'message': 'Something failed',
          'status_code': 500,
          'retryable': true,
        }
      };
      final exception = GatewayException.fromResponse(500, response);
      expect(exception.code, 'EXECUTION_ERROR');
      expect(exception.message, 'Something failed');
      expect(exception.retryable, true);
    });
  });

  group('StringUtils', () {
    test('truncation preserves empty strings', () {
      expect(StringUtils.truncate('', 10), '');
    });

    test('capitalization handles single characters', () {
      expect(StringUtils.capitalize('a'), 'A');
    });

    test('sanitize removes extra whitespace', () {
      expect(StringUtils.sanitize('  Hello   World  '), 'hello world');
    });
  });
}
