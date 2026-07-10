import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  SecureStorage() : _storage = const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  Future<void> save(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  Future<String?> read(String key) async {
    return await _storage.read(key: key);
  }

  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }

  Future<void> clear() async {
    await _storage.deleteAll();
  }

  Future<bool> hasSession() async {
    final token = await getSessionToken();
    return token != null && token.isNotEmpty;
  }

  Future<void> clearSession() async {
    await deleteSessionToken();
    await deleteRefreshToken();
  }

  Future<void> saveSessionToken(String token) async => save('session_token', token);
  Future<String?> getSessionToken() async => read('session_token');
  Future<void> deleteSessionToken() async => delete('session_token');

  Future<void> saveRefreshToken(String token) async => save('refresh_token', token);
  Future<String?> getRefreshToken() async => read('refresh_token');
  Future<void> deleteRefreshToken() async => delete('refresh_token');

  Future<void> saveWorkspaceId(String id) async => save('workspace_id', id);
  Future<String?> getWorkspaceId() async => read('workspace_id');

  Future<void> saveSubjectId(String id) async => save('subject_id', id);
  Future<String?> getSubjectId() async => read('subject_id');
}
