import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/presentation/pages/login_page.dart';
import 'package:jarvis_mobile/presentation/pages/diagnostics_page.dart';
import 'package:jarvis_mobile/presentation/pages/settings_page.dart';

void main() {
  group('LoginPage', () {
    testWidgets('renders login form', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginPage(),
          ),
        ),
      );

      expect(find.text('Sign In'), findsOneWidget);
      expect(find.byType(TextField), findsAtLeast(2));
    });
  });

  group('DiagnosticsPage', () {
    testWidgets('renders diagnostics heading', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: DiagnosticsPage(),
          ),
        ),
      );

      expect(find.text('Diagnostics'), findsOneWidget);
    });
  });

  group('SettingsPage', () {
    testWidgets('renders settings heading', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: SettingsPage(),
          ),
        ),
      );

      expect(find.text('Settings'), findsOneWidget);
    });
  });
}
