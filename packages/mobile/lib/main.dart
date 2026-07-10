import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jarvis_mobile/core/theme/app_theme.dart';
import 'package:jarvis_mobile/presentation/pages/home_page.dart';
import 'package:jarvis_mobile/presentation/pages/login_page.dart';
import 'package:jarvis_mobile/presentation/providers/auth_provider.dart';
import 'package:jarvis_mobile/presentation/providers/repository_providers.dart';
import 'package:jarvis_mobile/presentation/providers/theme_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  runApp(const ProviderScope(child: JarvisMobileApp()));
}

class JarvisMobileApp extends ConsumerStatefulWidget {
  const JarvisMobileApp({super.key});

  @override
  ConsumerState<JarvisMobileApp> createState() => _JarvisMobileAppState();
}

class _JarvisMobileAppState extends ConsumerState<JarvisMobileApp> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(authProvider.notifier).restoreSession();
      ref.read(authProvider.notifier).checkBiometrics();
      ref.read(themeProvider.notifier).loadPreference();
      ref.read(connectivityServiceProvider).initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = ref.watch(themeProvider);
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'JARVIS Mobile',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('de'),
        Locale('es'),
        Locale('fr'),
        Locale('ja'),
        Locale('ko'),
        Locale('pt'),
        Locale('zh'),
      ],
      home: authState.isAuthenticated ? const HomePage() : const LoginPage(),
    );
  }
}
