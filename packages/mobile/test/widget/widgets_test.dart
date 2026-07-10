import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/presentation/widgets/empty_state.dart';
import 'package:jarvis_mobile/presentation/widgets/loading_indicator.dart';
import 'package:jarvis_mobile/presentation/widgets/error_view.dart';
import 'package:jarvis_mobile/presentation/widgets/status_badge.dart';
import 'package:jarvis_mobile/presentation/widgets/section_header.dart';

void main() {
  group('EmptyState', () {
    testWidgets('renders message and icon', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyState(message: 'Nothing here', icon: Icons.info),
          ),
        ),
      );

      expect(find.text('Nothing here'), findsOneWidget);
      expect(find.byIcon(Icons.info), findsOneWidget);
    });

    testWidgets('renders action button when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmptyState(
              message: 'Nothing here',
              actionLabel: 'Retry',
              onAction: () {},
            ),
          ),
        ),
      );

      expect(find.text('Retry'), findsOneWidget);
    });
  });

  group('LoadingIndicator', () {
    testWidgets('renders spinner', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: LoadingIndicator()),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('renders with message', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: LoadingIndicator(message: 'Loading...')),
        ),
      );
      expect(find.text('Loading...'), findsOneWidget);
    });
  });

  group('ErrorView', () {
    testWidgets('renders error message and retry button', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ErrorView(
              message: 'Something went wrong',
              onRetry: () {},
            ),
          ),
        ),
      );

      expect(find.text('Something went wrong'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
  });

  group('StatusBadge', () {
    testWidgets('renders with label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: StatusBadge(label: 'Active', color: Colors.green)),
        ),
      );

      expect(find.text('Active'), findsOneWidget);
    });
  });

  group('SectionHeader', () {
    testWidgets('renders title', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: SectionHeader(title: 'My Section')),
        ),
      );

      expect(find.text('My Section'), findsOneWidget);
    });

    testWidgets('renders see all link when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SectionHeader(title: 'Section', onSeeAll: () {}),
          ),
        ),
      );

      expect(find.text('See all'), findsOneWidget);
    });
  });
}
