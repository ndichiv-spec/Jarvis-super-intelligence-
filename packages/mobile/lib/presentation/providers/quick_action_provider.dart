import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/quick_action.dart';
import 'package:jarvis_mobile/domain/repositories/quick_action_repository.dart';
import 'package:jarvis_mobile/domain/usecases/execute_quick_action_usecase.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class QuickActionState {
  final List<QuickAction> actions;
  final bool isLoading;

  const QuickActionState({
    this.actions = const [],
    this.isLoading = false,
  });

  QuickActionState copyWith({
    List<QuickAction>? actions,
    bool? isLoading,
  }) {
    return QuickActionState(
      actions: actions ?? this.actions,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class QuickActionNotifier extends StateNotifier<QuickActionState> {
  final QuickActionRepository _repository;
  final ExecuteQuickActionUseCase _executeUseCase;

  QuickActionNotifier({
    required QuickActionRepository repository,
    required ExecuteQuickActionUseCase executeUseCase,
  })  : _repository = repository,
        _executeUseCase = executeUseCase,
        super(const QuickActionState());

  Future<void> list() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.list();
      switch (result) {
        case Success<List<QuickAction>>():
          state = state.copyWith(actions: result.data, isLoading: false);
        case Failure<List<QuickAction>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> execute(String id) async {
    try {
      await _executeUseCase.call(id);
    } catch (_) {}
  }

  Future<void> reorder(List<String> ids) async {
    try {
      final result = await _repository.updateOrder(ids);
      if (result is Success<void>) {
        final reordered = <QuickAction>[];
        for (final id in ids) {
          final idx = state.actions.indexWhere((a) => a.id == id);
          if (idx >= 0) {
            reordered.add(state.actions[idx]);
          }
        }
        state = state.copyWith(
          actions: reordered.map((a) {
            final newOrder = reordered.indexOf(a);
            return QuickAction(
              id: a.id,
              label: a.label,
              iconName: a.iconName,
              actionType: a.actionType,
              actionPayload: a.actionPayload,
              order: newOrder,
              isEnabled: a.isEnabled,
            );
          }).toList(),
        );
      }
    } catch (_) {}
  }
}

final quickActionProvider =
    StateNotifierProvider<QuickActionNotifier, QuickActionState>((ref) {
  return QuickActionNotifier(
    repository: ref.watch(quickActionRepositoryProvider),
    executeUseCase: ref.watch(executeQuickActionUseCaseProvider),
  );
});
