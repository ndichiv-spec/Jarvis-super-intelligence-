import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/conversation_model.dart';
import 'package:jarvis_mobile/data/models/knowledge_document_model.dart';
import 'package:jarvis_mobile/data/models/project_model.dart';
import 'package:jarvis_mobile/data/models/workflow_model.dart';

class ProjectRemoteDataSource {
  ProjectRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<ProjectModel>> list(String workspaceId) async {
    final response = await httpClient.get(
      GatewayPaths.projectList,
      queryParams: {'workspaceId': workspaceId},
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => ProjectModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<ProjectModel> get(String id) async {
    final response = await httpClient.get('${GatewayPaths.projectDetail}$id');
    return response.dataOrThrow<ProjectModel>((json) => ProjectModel.fromJson(json as Map<String, dynamic>));
  }

  Future<List<ConversationModel>> getConversations(String projectId) async {
    final response = await httpClient.get(
      '${GatewayPaths.projectDetail}$projectId/conversations',
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => ConversationModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<List<WorkflowModel>> getWorkflows(String projectId) async {
    final response = await httpClient.get(
      '${GatewayPaths.projectDetail}$projectId/workflows',
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => WorkflowModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<List<KnowledgeDocumentModel>> getKnowledge(String projectId) async {
    final response = await httpClient.get(
      '${GatewayPaths.projectDetail}$projectId/knowledge',
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => KnowledgeDocumentModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }
}
