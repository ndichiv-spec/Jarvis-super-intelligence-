import 'dart:async';

import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/core/network/sse_client.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/conversation_remote_datasource.dart';
import 'package:jarvis_mobile/data/models/message_model.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/message.dart';
import 'package:jarvis_mobile/domain/repositories/conversation_repository.dart';

class ConversationRepositoryImpl implements ConversationRepository {
  ConversationRepositoryImpl({
    required this.remoteDataSource,
    required this.httpClient,
  });

  final ConversationRemoteDataSource remoteDataSource;
  final HttpClient httpClient;

  @override
  Future<Result<List<Conversation>>> list(String workspaceId, {int page = 1, int limit = 20}) async {
    try {
      final models = await remoteDataSource.list(workspaceId, page: page, limit: limit);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Conversation>> get(String id) async {
    try {
      final model = await remoteDataSource.get(id);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Conversation>> create(String title, {String? projectId}) async {
    try {
      final model = await remoteDataSource.create(title, projectId: projectId);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<Message>> sendMessage({
    required String conversationId,
    required String content,
    List<String>? attachmentIds,
  }) async {
    try {
      final model = await remoteDataSource.sendMessage(
        conversationId: conversationId,
        content: content,
        attachmentIds: attachmentIds,
      );
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Stream<Conversation> streamConversation(String id) {
    final sseClient = SseClient(baseUrl: httpClient.baseUrl);
    final stream = sseClient.stream(
      '${GatewayPaths.conversationStream}/$id',
      headers: httpClient.defaultHeaders,
    );

    return stream.map((event) {
      return Conversation(
        id: event['id'] as String? ?? id,
        title: event['title'] as String? ?? '',
        projectId: event['projectId'] as String?,
        workspaceId: event['workspaceId'] as String?,
        createdAt: event['createdAt'] != null
            ? DateTime.parse(event['createdAt'] as String)
            : DateTime.now(),
        updatedAt: event['updatedAt'] != null
            ? DateTime.parse(event['updatedAt'] as String)
            : DateTime.now(),
        messageCount: event['messageCount'] as int? ?? 0,
        isArchived: event['isArchived'] as bool? ?? false,
      );
    });
  }

  @override
  Future<Result<void>> delete(String id) async {
    try {
      await remoteDataSource.delete(id);
      return Result.success(null);
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
