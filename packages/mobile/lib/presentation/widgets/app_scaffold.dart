import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';

class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    this.title,
    this.actions,
    this.showBack = false,
    this.body,
    this.bottomNavigationBar,
    this.floatingActionButton,
  });

  final String? title;
  final List<Widget>? actions;
  final bool showBack;
  final Widget? body;
  final Widget? bottomNavigationBar;
  final Widget? floatingActionButton;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: title != null ? Text(title!) : null,
        actions: actions,
        leading: showBack ? const BackButton() : null,
      ),
      body: SafeArea(child: body ?? const SizedBox.shrink()),
      bottomNavigationBar: bottomNavigationBar,
      floatingActionButton: floatingActionButton,
    );
  }
}
