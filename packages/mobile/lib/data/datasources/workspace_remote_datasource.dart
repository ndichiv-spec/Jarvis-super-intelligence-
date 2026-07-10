import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/workspace_model.dart';

class WorkspaceRemoteDataSource {
  WorkspaceRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<WorkspaceModel> getCurrent() async {
    final response = await httpClient.get(GatewayPaths.workspaceCurrent);
    return response.dataOrThrow<WorkspaceModel>((json) => WorkspaceModel.fromJson(json as Map<String, dynamic>));
  }

  Future<List<WorkspaceModel>> list() async {
    final response = await httpClient.get(GatewayPaths.workspaceList);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => WorkspaceModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<void> setCurrent(String id) async {
    await httpClient.post(GatewayPaths.workspaceCurrent, body: {'workspaceId': id});
  }
}
