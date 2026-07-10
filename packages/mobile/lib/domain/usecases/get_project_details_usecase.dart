import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/entities/project.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/repositories/project_repository.dart';

class ProjectDetails {
  final Project project;
  final List<Conversation> conversations;
  final List<Workflow> workflows;
  final List<KnowledgeDocument> knowledge;

  const ProjectDetails({
    required this.project,
    required this.conversations,
    required this.workflows,
    required this.knowledge,
  });
}

class GetProjectDetailsUseCase {
  final ProjectRepository _projectRepository;

  GetProjectDetailsUseCase(this._projectRepository);

  Future<Result<ProjectDetails>> call(String projectId) async {
    final projectResult = await _projectRepository.get(projectId);
    if (projectResult is Failure) return Result.failure(projectResult.error);

    final project = (projectResult as Success<Project>).data;

    final results = await Future.wait([
      _projectRepository.getConversations(projectId),
      _projectRepository.getWorkflows(projectId),
      _projectRepository.getKnowledge(projectId),
    ]);

    final conversations = (results[0] as Success<List<Conversation>>).data;
    final workflows = (results[1] as Success<List<Workflow>>).data;
    final knowledge = (results[2] as Success<List<KnowledgeDocument>>).data;

    return Result.success(ProjectDetails(
      project: project,
      conversations: conversations,
      workflows: workflows,
      knowledge: knowledge,
    ));
  }
}
