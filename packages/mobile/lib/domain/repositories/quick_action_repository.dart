import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/quick_action.dart';

abstract class QuickActionRepository {
  Future<Result<List<QuickAction>>> list();
  Future<Result<void>> execute(String id);
  Future<Result<void>> updateOrder(List<String> ids);
}
