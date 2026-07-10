import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/entities/project.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';

abstract class ProjectRepository {
  Future<Result<List<Project>>> list(String workspaceId);
  Future<Result<Project>> get(String id);
  Future<Result<List<Conversation>>> getConversations(String projectId);
  Future<Result<List<Workflow>>> getWorkflows(String projectId);
  Future<Result<List<KnowledgeDocument>>> getKnowledge(String projectId);
}
