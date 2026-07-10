import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/workspace.dart';

abstract class WorkspaceRepository {
  Future<Result<Workspace>> getCurrent();
  Future<Result<List<Workspace>>> list();
  Future<Result<void>> setCurrent(String id);
}
