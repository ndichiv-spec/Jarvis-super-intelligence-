import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/entities/project.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/usecases/get_project_details_usecase.dart';
import 'package:jarvis_mobile/domain/usecases/get_projects_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class ProjectState {
  final List<Project> projects;
  final Project? currentProject;
  final List<Conversation> relatedConversations;
  final List<Workflow> relatedWorkflows;
  final List<KnowledgeDocument> relatedKnowledge;
  final bool isLoading;

  const ProjectState({
    this.projects = const [],
    this.currentProject,
    this.relatedConversations = const [],
    this.relatedWorkflows = const [],
    this.relatedKnowledge = const [],
    this.isLoading = false,
  });

  ProjectState copyWith({
    List<Project>? projects,
    Project? currentProject,
    List<Conversation>? relatedConversations,
    List<Workflow>? relatedWorkflows,
    List<KnowledgeDocument>? relatedKnowledge,
    bool? isLoading,
  }) {
    return ProjectState(
      projects: projects ?? this.projects,
      currentProject: currentProject ?? this.currentProject,
      relatedConversations: relatedConversations ?? this.relatedConversations,
      relatedWorkflows: relatedWorkflows ?? this.relatedWorkflows,
      relatedKnowledge: relatedKnowledge ?? this.relatedKnowledge,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class ProjectNotifier extends StateNotifier<ProjectState> {
  final GetProjectsUseCase _getProjectsUseCase;
  final GetProjectDetailsUseCase _getProjectDetailsUseCase;

  ProjectNotifier({
    required GetProjectsUseCase getProjectsUseCase,
    required GetProjectDetailsUseCase getProjectDetailsUseCase,
  })  : _getProjectsUseCase = getProjectsUseCase,
        _getProjectDetailsUseCase = getProjectDetailsUseCase,
        super(const ProjectState());

  Future<void> list(String workspaceId) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _getProjectsUseCase.call(workspaceId);
      switch (result) {
        case Success<List<Project>>():
          state = state.copyWith(projects: result.data, isLoading: false);
        case Failure<List<Project>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> select(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _getProjectDetailsUseCase.call(id);
      switch (result) {
        case Success<ProjectDetails>():
          state = state.copyWith(
            currentProject: result.data.project,
            relatedConversations: result.data.conversations,
            relatedWorkflows: result.data.workflows,
            relatedKnowledge: result.data.knowledge,
            isLoading: false,
          );
        case Failure<ProjectDetails>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }
}

final projectProvider = StateNotifierProvider<ProjectNotifier, ProjectState>((ref) {
  return ProjectNotifier(
    getProjectsUseCase: ref.watch(getProjectsUseCaseProvider),
    getProjectDetailsUseCase: ref.watch(getProjectDetailsUseCaseProvider),
  );
});
