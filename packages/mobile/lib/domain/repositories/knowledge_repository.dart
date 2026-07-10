import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_collection.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';

abstract class KnowledgeRepository {
  Future<Result<List<KnowledgeDocument>>> search(String query, {String? collectionId});
  Future<Result<KnowledgeDocument>> getDocument(String id);
  Future<Result<List<KnowledgeCollection>>> listCollections();
  Future<Result<KnowledgeCollection>> getCollection(String id);
}
