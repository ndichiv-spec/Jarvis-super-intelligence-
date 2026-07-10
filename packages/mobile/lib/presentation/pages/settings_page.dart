import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/presentation/providers/settings_provider.dart';
import 'package:jarvis_mobile/presentation/providers/theme_provider.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final themeMode = ref.watch(themeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: AppSpacing.paddingMd,
        children: [
          Semantics(
            header: true,
            child: Text('Appearance', style: context.textTheme.titleSmall?.copyWith(
              color: context.colorScheme.primary,
              fontWeight: FontWeight.w600,
            )),
          ),
          const SizedBox(height: AppSpacing.sm),
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Dark Mode'),
                  subtitle: const Text('Toggle dark theme'),
                  value: themeMode == ThemeMode.dark,
                  onChanged: (v) => ref.read(themeProvider.notifier).setThemeMode(
                    v ? ThemeMode.dark : ThemeMode.light,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Semantics(
            header: true,
            child: Text('Preferences', style: context.textTheme.titleSmall?.copyWith(
              color: context.colorScheme.primary,
              fontWeight: FontWeight.w600,
            )),
          ),
          const SizedBox(height: AppSpacing.sm),
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Biometric Authentication'),
                  subtitle: const Text('Use fingerprint or face to unlock'),
                  value: settings.biometricEnabled,
                  onChanged: (v) => ref.read(settingsProvider.notifier).updateSetting('biometricEnabled', v),
                ),
                const Divider(height: 1, indent: AppSpacing.md, endIndent: AppSpacing.md),
                SwitchListTile(
                  title: const Text('Notifications'),
                  subtitle: const Text('Receive push notifications'),
                  value: settings.notificationsEnabled,
                  onChanged: (v) => ref.read(settingsProvider.notifier).updateSetting('notificationsEnabled', v),
                ),
                const Divider(height: 1, indent: AppSpacing.md, endIndent: AppSpacing.md),
                SwitchListTile(
                  title: const Text('Offline Mode'),
                  subtitle: const Text('Enable offline support'),
                  value: settings.offlineModeEnabled,
                  onChanged: (v) => ref.read(settingsProvider.notifier).updateSetting('offlineModeEnabled', v),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Semantics(
            header: true,
            child: Text('Account', style: context.textTheme.titleSmall?.copyWith(
              color: context.colorScheme.primary,
              fontWeight: FontWeight.w600,
            )),
          ),
          const SizedBox(height: AppSpacing.sm),
          Card(
            child: ListTile(
              leading: const Icon(Icons.language_rounded),
              title: const Text('Language'),
              subtitle: const Text('English'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {},
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Semantics(
            header: true,
            child: Text('About', style: context.textTheme.titleSmall?.copyWith(
              color: context.colorScheme.primary,
              fontWeight: FontWeight.w600,
            )),
          ),
          const SizedBox(height: AppSpacing.sm),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('Version'),
                  subtitle: const Text('1.0.0+1'),
                ),
                const Divider(height: 1, indent: AppSpacing.md, endIndent: AppSpacing.md),
                ListTile(
                  leading: const Icon(Icons.description_outlined),
                  title: const Text('Licenses'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => showLicensePage(context: context),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
