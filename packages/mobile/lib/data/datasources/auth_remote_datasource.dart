import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/session_model.dart';

class AuthRemoteDataSource {
  AuthRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<SessionModel> login(String email, String password) async {
    final response = await httpClient.post(
      GatewayPaths.authLogin,
      body: {'email': email, 'password': password},
    );
    return response.dataOrThrow<SessionModel>((json) => SessionModel.fromJson(json as Map<String, dynamic>));
  }

  Future<SessionModel> loginWithBiometric() async {
    final response = await httpClient.post(GatewayPaths.authBiometric);
    return response.dataOrThrow<SessionModel>((json) => SessionModel.fromJson(json as Map<String, dynamic>));
  }

  Future<void> logout() async {
    await httpClient.post(GatewayPaths.authLogout);
  }

  Future<SessionModel> refreshSession() async {
    final response = await httpClient.post(GatewayPaths.authRefresh);
    return response.dataOrThrow<SessionModel>((json) => SessionModel.fromJson(json as Map<String, dynamic>));
  }

  Future<SessionModel?> getSession() async {
    final response = await httpClient.get(GatewayPaths.authLogin);
    return response.data<SessionModel>((json) => SessionModel.fromJson(json as Map<String, dynamic>));
  }
}
