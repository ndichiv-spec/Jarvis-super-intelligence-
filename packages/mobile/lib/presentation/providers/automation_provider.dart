import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/entities/workflow_execution.dart';
import 'package:jarvis_mobile/domain/repositories/automation_repository.dart';
import 'package:jarvis_mobile/domain/usecases/manage_workflow_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class AutomationState {
  final List<Workflow> workflows;
  final Workflow? currentWorkflow;
  final List<WorkflowExecution> history;
  final bool isLoading;

  const AutomationState({
    this.workflows = const [],
    this.currentWorkflow,
    this.history = const [],
    this.isLoading = false,
  });

  AutomationState copyWith({
    List<Workflow>? workflows,
    Workflow? currentWorkflow,
    List<WorkflowExecution>? history,
    bool? isLoading,
  }) {
    return AutomationState(
      workflows: workflows ?? this.workflows,
      currentWorkflow: currentWorkflow ?? this.currentWorkflow,
      history: history ?? this.history,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class AutomationNotifier extends StateNotifier<AutomationState> {
  final AutomationRepository _repository;
  final ManageWorkflowUseCase _manageWorkflowUseCase;

  AutomationNotifier({
    required AutomationRepository repository,
    required ManageWorkflowUseCase manageWorkflowUseCase,
  })  : _repository = repository,
        _manageWorkflowUseCase = manageWorkflowUseCase,
        super(const AutomationState());

  Future<void> list() async {
    state = state.copyWith(isLoading: true);
    try {
      final results = await Future.wait([
        _repository.listWorkflows(),
        _repository.getHistory(),
      ]);
      final workflowsResult = results[0];
      final historyResult = results[1];
      if (workflowsResult is Success<List<Workflow>>) {
        state = state.copyWith(workflows: workflowsResult.data);
      }
      if (historyResult is Success<List<WorkflowExecution>>) {
        state = state.copyWith(history: historyResult.data);
      }
      state = state.copyWith(isLoading: false);
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> select(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.getWorkflow(id);
      switch (result) {
        case Success<Workflow>():
          state = state.copyWith(currentWorkflow: result.data, isLoading: false);
        case Failure<Workflow>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> pause(String id) async {
    try {
      final result = await _manageWorkflowUseCase.pause(id);
      if (result is Success<void>) {
        state = state.copyWith(
          workflows: state.workflows.map((w) {
            if (w.id == id) {
              return Workflow(
                id: w.id,
                name: w.name,
                description: w.description,
                status: WorkflowStatus.paused,
                trigger: w.trigger,
                lastRunAt: w.lastRunAt,
                nextRunAt: w.nextRunAt,
                createdAt: w.createdAt,
              );
            }
            return w;
          }).toList(),
        );
      }
    } catch (_) {}
  }

  Future<void> resume(String id) async {
    try {
      final result = await _manageWorkflowUseCase.resume(id);
      if (result is Success<void>) {
        state = state.copyWith(
          workflows: state.workflows.map((w) {
            if (w.id == id) {
              return Workflow(
                id: w.id,
                name: w.name,
                description: w.description,
                status: WorkflowStatus.idle,
                trigger: w.trigger,
                lastRunAt: w.lastRunAt,
                nextRunAt: w.nextRunAt,
                createdAt: w.createdAt,
              );
            }
            return w;
          }).toList(),
        );
      }
    } catch (_) {}
  }

  Future<void> cancelExecution(String id) async {
    try {
      await _manageWorkflowUseCase.cancel(id);
    } catch (_) {}
  }
}

final automationProvider =
    StateNotifierProvider<AutomationNotifier, AutomationState>((ref) {
  return AutomationNotifier(
    repository: ref.watch(automationRepositoryProvider),
    manageWorkflowUseCase: ref.watch(manageWorkflowUseCaseProvider),
  );
});
