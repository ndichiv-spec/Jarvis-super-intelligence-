import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/conversation_model.dart';
import 'package:jarvis_mobile/data/models/message_model.dart';

class ConversationRemoteDataSource {
  ConversationRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<ConversationModel>> list(String workspaceId, {int page = 1, int limit = 20}) async {
    final response = await httpClient.get(
      GatewayPaths.conversationList,
      queryParams: {'workspaceId': workspaceId, 'page': page.toString(), 'limit': limit.toString()},
    );
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => ConversationModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<ConversationModel> get(String id) async {
    final response = await httpClient.get('${GatewayPaths.conversationList}/$id');
    return response.dataOrThrow<ConversationModel>((json) => ConversationModel.fromJson(json as Map<String, dynamic>));
  }

  Future<ConversationModel> create(String title, {String? projectId}) async {
    final body = <String, dynamic>{'title': title};
    if (projectId != null) {
      body['projectId'] = projectId;
    }
    final response = await httpClient.post(GatewayPaths.conversationCreate, body: body);
    return response.dataOrThrow<ConversationModel>((json) => ConversationModel.fromJson(json as Map<String, dynamic>));
  }

  Future<MessageModel> sendMessage({
    required String conversationId,
    required String content,
    List<String>? attachmentIds,
  }) async {
    final body = <String, dynamic>{'content': content};
    if (attachmentIds != null && attachmentIds.isNotEmpty) {
      body['attachmentIds'] = attachmentIds;
    }
    final response = await httpClient.post(
      '${GatewayPaths.conversationMessages}$conversationId/messages',
      body: body,
    );
    return response.dataOrThrow<MessageModel>((json) => MessageModel.fromJson(json as Map<String, dynamic>));
  }

  Future<void> delete(String id) async {
    await httpClient.delete('${GatewayPaths.conversationList}/$id');
  }
}
