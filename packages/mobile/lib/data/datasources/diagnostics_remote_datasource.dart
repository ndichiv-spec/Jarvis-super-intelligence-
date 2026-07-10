import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/app_health_model.dart';

class DiagnosticsRemoteDataSource {
  DiagnosticsRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<AppHealthModel> getHealth() async {
    final response = await httpClient.get(GatewayPaths.diagnosticsHealth);
    return response.dataOrThrow<AppHealthModel>((json) => AppHealthModel.fromJson(json as Map<String, dynamic>));
  }

  Future<Map<String, dynamic>> getStats() async {
    final response = await httpClient.get(GatewayPaths.diagnosticsStats);
    return response.dataOrThrow<Map<String, dynamic>>((json) => json as Map<String, dynamic>);
  }
}
