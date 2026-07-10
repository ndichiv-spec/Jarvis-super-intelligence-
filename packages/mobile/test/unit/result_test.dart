import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/core/utils/result.dart';

void main() {
  group('Result', () {
    test('Success holds data', () {
      const result = Success<int>(42);
      expect(result.data, 42);
      expect(result, isA<Success<int>>());
    });

    test('Failure holds error', () {
      final error = Exception('test error');
      final result = Failure<int>(error);
      expect(result.error, error);
      expect(result, isA<Failure<int>>());
    });

    test('Success and Failure are different types', () {
      const success = Success<int>(1);
      final failure = Failure<int>(Exception(''));
      expect(success, isNot(isA<Failure>()));
      expect(failure, isA<Failure>());
    });

    test('Success equality works', () {
      const a = Success<int>(1);
      const b = Success<int>(1);
      const c = Success<int>(2);
      expect(a, equals(b));
      expect(a, isNot(equals(c)));
    });
  });
}
