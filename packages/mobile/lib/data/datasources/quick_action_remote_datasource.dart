import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/quick_action_model.dart';

class QuickActionRemoteDataSource {
  QuickActionRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<QuickActionModel>> list() async {
    final response = await httpClient.get(GatewayPaths.quickActions);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => QuickActionModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<void> execute(String id) async {
    await httpClient.post('${GatewayPaths.quickActions}/$id/execute');
  }

  Future<void> updateOrder(List<String> ids) async {
    await httpClient.put('${GatewayPaths.quickActions}/order', body: {'ids': ids});
  }
}
