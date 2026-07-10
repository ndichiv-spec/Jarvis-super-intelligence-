import 'package:flutter/foundation.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_collection.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/repositories/knowledge_repository.dart';
import 'package:riverpod/riverpod.dart';

import 'repository_providers.dart';

@immutable
class KnowledgeState {
  final List<KnowledgeCollection> collections;
  final List<KnowledgeDocument> documents;
  final KnowledgeCollection? currentCollection;
  final List<KnowledgeDocument> searchResults;
  final String query;
  final bool isLoading;

  const KnowledgeState({
    this.collections = const [],
    this.documents = const [],
    this.currentCollection,
    this.searchResults = const [],
    this.query = '',
    this.isLoading = false,
  });

  KnowledgeState copyWith({
    List<KnowledgeCollection>? collections,
    List<KnowledgeDocument>? documents,
    KnowledgeCollection? currentCollection,
    List<KnowledgeDocument>? searchResults,
    String? query,
    bool? isLoading,
  }) {
    return KnowledgeState(
      collections: collections ?? this.collections,
      documents: documents ?? this.documents,
      currentCollection: currentCollection ?? this.currentCollection,
      searchResults: searchResults ?? this.searchResults,
      query: query ?? this.query,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class KnowledgeNotifier extends StateNotifier<KnowledgeState> {
  final KnowledgeRepository _repository;

  KnowledgeNotifier(this._repository) : super(const KnowledgeState());

  Future<void> listCollections() async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.listCollections();
      switch (result) {
        case Success<List<KnowledgeCollection>>():
          state = state.copyWith(collections: result.data, isLoading: false);
        case Failure<List<KnowledgeCollection>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> selectCollection(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.getCollection(id);
      switch (result) {
        case Success<KnowledgeCollection>():
          state = state.copyWith(currentCollection: result.data, isLoading: false);
        case Failure<KnowledgeCollection>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> search(String query) async {
    state = state.copyWith(isLoading: true, query: query);
    try {
      final result = await _repository.search(
        query,
        collectionId: state.currentCollection?.id,
      );
      switch (result) {
        case Success<List<KnowledgeDocument>>():
          state = state.copyWith(
            searchResults: result.data,
            documents: result.data,
            isLoading: false,
          );
        case Failure<List<KnowledgeDocument>>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> getDocument(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.getDocument(id);
      switch (result) {
        case Success<KnowledgeDocument>():
          state = state.copyWith(
            documents: [result.data],
            isLoading: false,
          );
        case Failure<KnowledgeDocument>():
          state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }
}

final knowledgeProvider = StateNotifierProvider<KnowledgeNotifier, KnowledgeState>((ref) {
  return KnowledgeNotifier(ref.watch(knowledgeRepositoryProvider));
});
