import 'package:jarvis_mobile/core/errors/app_exception.dart';
import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/data/datasources/knowledge_remote_datasource.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_collection.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';
import 'package:jarvis_mobile/domain/repositories/knowledge_repository.dart';

class KnowledgeRepositoryImpl implements KnowledgeRepository {
  KnowledgeRepositoryImpl({required this.remoteDataSource});

  final KnowledgeRemoteDataSource remoteDataSource;

  @override
  Future<Result<List<KnowledgeDocument>>> search(String query, {String? collectionId}) async {
    try {
      final models = await remoteDataSource.search(query, collectionId: collectionId);
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<KnowledgeDocument>> getDocument(String id) async {
    try {
      final model = await remoteDataSource.getDocument(id);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<List<KnowledgeCollection>>> listCollections() async {
    try {
      final models = await remoteDataSource.listCollections();
      return Result.success(models.map((e) => e.toEntity()).toList());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }

  @override
  Future<Result<KnowledgeCollection>> getCollection(String id) async {
    try {
      final model = await remoteDataSource.getCollection(id);
      return Result.success(model.toEntity());
    } on AppException catch (e) {
      return Result.failure(e);
    }
  }
}
