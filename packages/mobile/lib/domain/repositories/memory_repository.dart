import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/memory_item.dart';

abstract class MemoryRepository {
  Future<Result<List<MemoryItem>>> list({int page = 1, int limit = 20});
  Future<Result<List<MemoryItem>>> search(String query);
  Future<Result<void>> archive(String id);
  Future<Result<void>> delete(String id);
  Future<Result<MemoryItem>> get(String id);
}
