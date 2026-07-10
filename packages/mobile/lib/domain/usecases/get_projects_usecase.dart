import 'package:jarvis_mobile/core/utils/result.dart';
import 'package:jarvis_mobile/domain/entities/project.dart';
import 'package:jarvis_mobile/domain/repositories/project_repository.dart';

class GetProjectsUseCase {
  final ProjectRepository _projectRepository;

  GetProjectsUseCase(this._projectRepository);

  Future<Result<List<Project>>> call(String workspaceId) {
    return _projectRepository.list(workspaceId);
  }
}
