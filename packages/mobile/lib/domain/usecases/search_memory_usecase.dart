import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/memory_item.dart';
import 'package:jarvis_mobile/domain/repositories/memory_repository.dart';

class SearchMemoryUseCase {
  final MemoryRepository _memoryRepository;

  SearchMemoryUseCase(this._memoryRepository);

  Future<Result<List<MemoryItem>>> call(String query) {
    return _memoryRepository.search(query);
  }
}
