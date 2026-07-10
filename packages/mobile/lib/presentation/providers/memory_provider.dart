import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/memory_item.dart';
import 'package:jarvis_mobile/domain/repositories/memory_repository.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class MemoryState {
  final List<MemoryItem> items;
  final String query;
  final bool isLoading;

  const MemoryState({
    this.items = const [],
    this.query = '',
    this.isLoading = false,
  });

  MemoryState copyWith({
    List<MemoryItem>? items,
    String? query,
    bool? isLoading,
  }) {
    return MemoryState(
      items: items ?? this.items,
      query: query ?? this.query,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class MemoryNotifier extends StateNotifier<MemoryState> {
  final MemoryRepository _repository;

  MemoryNotifier(this._repository) : super(const MemoryState());

  Future<void> list() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.list();
      switch (result) {
        case Success<List<MemoryItem>>():
          state = state.copyWith(items: result.data, isLoading: false);
        case Failure<List<MemoryItem>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> search(String query) async {
    state = state.copyWith(isLoading: true, query: query);
    try {
      final result = await _repository.search(query);
      switch (result) {
        case Success<List<MemoryItem>>():
          state = state.copyWith(items: result.data, isLoading: false);
        case Failure<List<MemoryItem>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> archive(String id) async {
    try {
      final result = await _repository.archive(id);
      if (result is Success<void>) {
        state = state.copyWith(
          items: state.items.where((item) => item.id != id).toList(),
        );
      }
    } catch (_) {}
  }

  Future<void> delete(String id) async {
    try {
      final result = await _repository.delete(id);
      if (result is Success<void>) {
        state = state.copyWith(
          items: state.items.where((item) => item.id != id).toList(),
        );
      }
    } catch (_) {}
  }
}

final memoryProvider = StateNotifierProvider<MemoryNotifier, MemoryState>((ref) {
  return MemoryNotifier(ref.watch(memoryRepositoryProvider));
});
