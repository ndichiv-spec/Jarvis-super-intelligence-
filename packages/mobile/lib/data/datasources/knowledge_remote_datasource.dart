import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/knowledge_collection_model.dart';
import 'package:jarvis_mobile/data/models/knowledge_document_model.dart';

class KnowledgeRemoteDataSource {
  KnowledgeRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<KnowledgeDocumentModel>> search(String query, {String? collectionId}) async {
    final params = <String, String>{'q': query};
    if (collectionId != null) {
      params['collectionId'] = collectionId;
    }
    final response = await httpClient.get(GatewayPaths.knowledgeSearch, queryParams: params);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => KnowledgeDocumentModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<KnowledgeDocumentModel> getDocument(String id) async {
    final response = await httpClient.get('${GatewayPaths.knowledgeDocument}$id');
    return response.dataOrThrow<KnowledgeDocumentModel>((json) => KnowledgeDocumentModel.fromJson(json as Map<String, dynamic>));
  }

  Future<List<KnowledgeCollectionModel>> listCollections() async {
    final response = await httpClient.get(GatewayPaths.knowledgeCollections);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => KnowledgeCollectionModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<KnowledgeCollectionModel> getCollection(String id) async {
    final response = await httpClient.get('${GatewayPaths.knowledgeCollections}/$id');
    return response.dataOrThrow<KnowledgeCollectionModel>((json) => KnowledgeCollectionModel.fromJson(json as Map<String, dynamic>));
  }
}
