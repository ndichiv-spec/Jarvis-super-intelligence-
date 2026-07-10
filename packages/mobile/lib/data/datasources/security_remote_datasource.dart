import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/device_model.dart';
import 'package:jarvis_mobile/data/models/session_model.dart';

class SecurityRemoteDataSource {
  SecurityRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<SessionModel>> listSessions() async {
    final response = await httpClient.get(GatewayPaths.sessionList);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => SessionModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<void> revokeSession(String id) async {
    await httpClient.post('${GatewayPaths.sessionRevoke}/$id');
  }

  Future<List<DeviceModel>> listDevices() async {
    final response = await httpClient.get(GatewayPaths.deviceList);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => DeviceModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<DeviceModel> registerDevice(String name, String type) async {
    final response = await httpClient.post(
      GatewayPaths.deviceRegister,
      body: {'name': name, 'type': type},
    );
    return response.dataOrThrow<DeviceModel>((json) => DeviceModel.fromJson(json as Map<String, dynamic>));
  }

  Future<void> trustDevice(String id) async {
    await httpClient.put('${GatewayPaths.deviceList}/$id/trust');
  }

  Future<void> removeDevice(String id) async {
    await httpClient.delete('${GatewayPaths.deviceList}/$id');
  }
}
