import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/security/biometric_auth.dart';
import 'package:jarvis_mobile/core/security/secure_storage.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/entities/user.dart';
import 'package:jarvis_mobile/domain/usecases/login_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/logout_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class AuthState {
  final User? user;
  final Session? session;
  final bool isAuthenticated;
  final bool isBiometricAvailable;
  final bool isLoading;
  final String? error;

  const AuthState({
    this.user,
    this.session,
    this.isAuthenticated = false,
    this.isBiometricAvailable = false,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    Session? session,
    bool? isAuthenticated,
    bool? isBiometricAvailable,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return AuthState(
      user: user ?? this.user,
      session: session ?? this.session,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isBiometricAvailable: isBiometricAvailable ?? this.isBiometricAvailable,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final LoginUseCase _loginUseCase;
  final LogoutUseCase _logoutUseCase;
  final SecureStorage _secureStorage;
  final BiometricAuth _biometricAuth;

  AuthNotifier({
    required LoginUseCase loginUseCase,
    required LogoutUseCase logoutUseCase,
    required SecureStorage secureStorage,
    required BiometricAuth biometricAuth,
  })  : _loginUseCase = loginUseCase,
        _logoutUseCase = logoutUseCase,
        _secureStorage = secureStorage,
        _biometricAuth = biometricAuth,
        super(const AuthState());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final result = await _loginUseCase.call(email, password);
      switch (result) {
        case Success<Session>():
          await _secureStorage.saveSessionToken(result.data.token);
          await _secureStorage.saveRefreshToken(result.data.refreshToken);
          state = state.copyWith(
            session: result.data,
            isAuthenticated: true,
            isLoading: false,
            clearError: true,
          );
        case Failure<Session>():
          state = state.copyWith(
            isLoading: false,
            error: result.error.message,
          );
      }
    } on AppException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loginWithBiometric() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final authenticated = await _biometricAuth.authenticate(
        reason: 'Authenticate to access JARVIS',
      );
      if (!authenticated) {
        state = state.copyWith(isLoading: false, error: 'Biometric authentication cancelled');
        return;
      }
      state = state.copyWith(isLoading: false, clearError: true);
    } on AppException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> logout() async {
    state = state.copyWith(isLoading: true);
    try {
      await _logoutUseCase.call();
      await _secureStorage.clearSession();
      state = const AuthState();
    } on AppException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> restoreSession() async {
    state = state.copyWith(isLoading: true);
    try {
      final hasSession = await _secureStorage.hasSession();
      state = state.copyWith(
        isAuthenticated: hasSession,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> checkBiometrics() async {
    try {
      final available = await _biometricAuth.canCheckBiometrics();
      state = state.copyWith(isBiometricAvailable: available);
    } catch (_) {
      state = state.copyWith(isBiometricAvailable: false);
    }
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    loginUseCase: ref.watch(loginUseCaseProvider),
    logoutUseCase: ref.watch(logoutUseCaseProvider),
    secureStorage: ref.watch(secureStorageProvider),
    biometricAuth: ref.watch(biometricAuthServiceProvider),
  );
});
