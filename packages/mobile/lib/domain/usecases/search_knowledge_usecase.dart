import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/repositories/knowledge_repository.dart';

class SearchKnowledgeUseCase {
  final KnowledgeRepository _knowledgeRepository;

  SearchKnowledgeUseCase(this._knowledgeRepository);

  Future<Result<List<KnowledgeDocument>>> call(
    String query, {
    String? collectionId,
  }) {
    return _knowledgeRepository.search(query, collectionId: collectionId);
  }
}
