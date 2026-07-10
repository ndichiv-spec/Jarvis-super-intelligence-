import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/app_settings_model.dart';

class SettingsRemoteDataSource {
  SettingsRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<AppSettingsModel> get() async {
    final response = await httpClient.get(GatewayPaths.settingsGet);
    return response.dataOrThrow<AppSettingsModel>((json) => AppSettingsModel.fromJson(json as Map<String, dynamic>));
  }

  Future<void> update(AppSettingsModel settings) async {
    await httpClient.put(GatewayPaths.settingsUpdate, body: settings.toJson());
  }
}
