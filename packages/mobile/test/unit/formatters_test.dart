import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/core/utils/formatters.dart';

void main() {
  group('StringUtils', () {
    test('truncate', () {
      expect(StringUtils.truncate('hello world', 5), 'hello...');
      expect(StringUtils.truncate('hi', 5), 'hi');
      expect(StringUtils.truncate('', 5), '');
    });

    test('capitalize', () {
      expect(StringUtils.capitalize('hello'), 'Hello');
      expect(StringUtils.capitalize(''), '');
      expect(StringUtils.capitalize('a'), 'A');
    });

    test('sanitize', () {
      expect(StringUtils.sanitize('Hello  World!'), 'hello world');
      expect(StringUtils.sanitize('  Test  '), 'test');
    });
  });

  group('DurationFormatter', () {
    test('format seconds', () {
      expect(DurationFormatter.format(const Duration(seconds: 30)), '30s');
    });

    test('format minutes', () {
      expect(DurationFormatter.format(const Duration(minutes: 5)), '5m');
    });

    test('format hours', () {
      expect(DurationFormatter.format(const Duration(hours: 2, minutes: 30)), '2h 30m');
    });
  });

  group('ByteFormatter', () {
    test('formats bytes', () {
      expect(ByteFormatter.format(500), '500 B');
    });

    test('formats KB', () {
      expect(ByteFormatter.format(2048), '2.0 KB');
    });

    test('formats MB', () {
      expect(ByteFormatter.format(1048576), '1.0 MB');
    });
  });
}
