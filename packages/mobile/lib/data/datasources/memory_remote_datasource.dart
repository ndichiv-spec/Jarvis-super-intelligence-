import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/memory_item_model.dart';

class MemoryRemoteDataSource {
  MemoryRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<MemoryItemModel>> list({int page = 1, int limit = 20}) async {
    final response = await httpClient.get(
      GatewayPaths.memoryList,
      queryParams: {'page': page.toString(), 'limit': limit.toString()},
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => MemoryItemModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<List<MemoryItemModel>> search(String query) async {
    final response = await httpClient.get(
      GatewayPaths.memorySearch,
      queryParams: {'q': query},
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => MemoryItemModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<MemoryItemModel> get(String id) async {
    final response = await httpClient.get('${GatewayPaths.memoryList}/$id');
    return response.dataOrThrow<MemoryItemModel>((json) => MemoryItemModel.fromJson(json as Map<String, dynamic>));
  }

  Future<void> archive(String id) async {
    await httpClient.put('${GatewayPaths.memoryArchive}/$id');
  }

  Future<void> delete(String id) async {
    await httpClient.delete('${GatewayPaths.memoryList}/$id');
  }
}
