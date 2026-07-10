import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/workspace.dart';
import 'package:jarvis_mobile/domain/repositories/workspace_repository.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class WorkspaceState {
  final Workspace? currentWorkspace;
  final List<Workspace> workspaces;
  final bool isLoading;

  const WorkspaceState({
    this.currentWorkspace,
    this.workspaces = const [],
    this.isLoading = false,
  });

  WorkspaceState copyWith({
    Workspace? currentWorkspace,
    List<Workspace>? workspaces,
    bool? isLoading,
  }) {
    return WorkspaceState(
      currentWorkspace: currentWorkspace ?? this.currentWorkspace,
      workspaces: workspaces ?? this.workspaces,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class WorkspaceNotifier extends StateNotifier<WorkspaceState> {
  final WorkspaceRepository _repository;

  WorkspaceNotifier(this._repository) : super(const WorkspaceState());

  Future<void> loadWorkspaces() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.list();
      switch (result) {
        case Success<List<Workspace>>():
          state = state.copyWith(workspaces: result.data, isLoading: false);
        case Failure<List<Workspace>>():
          state = state.copyWith(isLoading: false);
      }
      final currentResult = await _repository.getCurrent();
      if (currentResult is Success<Workspace>) {
        state = state.copyWith(currentWorkspace: currentResult.data);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> setCurrentWorkspace(String id) async {
    try {
      final result = await _repository.setCurrent(id);
      if (result is Success<void>) {
        final idx = state.workspaces.indexWhere((w) => w.id == id);
        if (idx >= 0) {
          state = state.copyWith(currentWorkspace: state.workspaces[idx]);
        }
      }
    } catch (_) {}
  }
}

final workspaceProvider = StateNotifierProvider<WorkspaceNotifier, WorkspaceState>((ref) {
  return WorkspaceNotifier(ref.watch(workspaceRepositoryProvider));
});
