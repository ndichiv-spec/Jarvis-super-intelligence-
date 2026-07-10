import 'package:jarvis_mobile/core/network/connectivity_service.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

final connectivityProvider = StreamProvider<bool>((ref) {
  final service = ref.watch(connectivityServiceProvider);
  ref.onDispose(() => service.dispose());
  return service.onConnectivityChanged;
});
