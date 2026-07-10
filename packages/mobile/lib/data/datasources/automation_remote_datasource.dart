import 'package:jarvis_mobile/core/constants/gateway_paths.dart';
import 'package:jarvis_mobile/core/network/http_client.dart';
import 'package:jarvis_mobile/data/models/workflow_execution_model.dart';
import 'package:jarvis_mobile/data/models/workflow_model.dart';

class AutomationRemoteDataSource {
  AutomationRemoteDataSource({required this.httpClient});

  final HttpClient httpClient;

  Future<List<WorkflowModel>> listWorkflows() async {
    final response = await httpClient.get(GatewayPaths.automationList);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => WorkflowModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<WorkflowModel> getWorkflow(String id) async {
    final response = await httpClient.get('${GatewayPaths.automationDetail}$id');
    return response.dataOrThrow<WorkflowModel>((json) => WorkflowModel.fromJson(json as Map<String, dynamic>));
  }

  Future<List<WorkflowExecutionModel>> getHistory({String? workflowId, int page = 1, int limit = 20}) async {
    final params = <String, String>{'page': page.toString(), 'limit': limit.toString()};
    if (workflowId != null) {
      params['workflowId'] = workflowId;
    }
    final response = await httpClient.get(GatewayPaths.automationHistory, queryParams: params);
    final data = response.data<List<dynamic>>((json) => json as List<dynamic>);
    return data?.map((e) => WorkflowExecutionModel.fromJson(e as Map<String, dynamic>)).toList() ?? [];
  }

  Future<void> pauseWorkflow(String id) async {
    await httpClient.post(
      '${GatewayPaths.automationAction}/pause',
      body: {'workflowId': id},
    );
  }

  Future<void> resumeWorkflow(String id) async {
    await httpClient.post(
      '${GatewayPaths.automationAction}/resume',
      body: {'workflowId': id},
    );
  }

  Future<void> cancelExecution(String id) async {
    await httpClient.post(
      '${GatewayPaths.automationAction}/cancel',
      body: {'executionId': id},
    );
  }
}
