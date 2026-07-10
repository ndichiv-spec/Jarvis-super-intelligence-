import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/app_settings_model.dart';
import 'package:jarvis_mobile/data/models/notification_model.dart';

class NotificationRemoteDataSource {
  NotificationRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<NotificationModel>> list({int page = 1, int limit = 20}) async {
    final response = await httpClient.get(
      GatewayPaths.notificationList,
      queryParams: {'page': page.toString(), 'limit': limit.toString()},
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => NotificationModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<void> markRead(String id) async {
    await httpClient.put('${GatewayPaths.notificationMarkRead}/$id');
  }

  Future<void> markAllRead() async {
    await httpClient.put(GatewayPaths.notificationMarkRead);
  }

  Future<AppSettingsModel> getSettings() async {
    final response = await httpClient.get(GatewayPaths.notificationSettings);
    return response.dataOrThrow<AppSettingsModel>((json) => AppSettingsModel.fromJson(json as Map<String, dynamic>));
  }

  Future<void> updateSettings(AppSettingsModel settings) async {
    await httpClient.put(GatewayPaths.notificationSettings, body: settings.toJson());
  }
}
