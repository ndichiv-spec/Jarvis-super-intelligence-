import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/session.dart';
import 'package:jarvis_mobile/domain/entities/user.dart';

abstract class AuthRepository {
  Future<Result<Session>> login(String email, String password);
  Future<Result<Session>> loginWithBiometric();
  Future<Result<void>> logout();
  Future<Result<Session>> refreshSession();
  Future<Result<Session?>> getSession();
  Future<Result<bool>> isAuthenticated();
}
