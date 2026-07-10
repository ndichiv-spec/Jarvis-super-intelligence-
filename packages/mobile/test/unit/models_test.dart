import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/data/models/session_model.dart';
import 'package:jarvis_mobile/data/models/user_model.dart';
import 'package:jarvis_mobile/data/models/conversation_model.dart';
import 'package:jarvis_mobile/data/models/message_model.dart';
import 'package:jarvis_mobile/data/models/project_model.dart';
import 'package:jarvis_mobile/data/models/workflow_model.dart';
import 'package:jarvis_mobile/data/models/app_health_model.dart';

void main() {
  group('Model serialization', () {
    test('SessionModel roundtrip', () {
      final model = SessionModel(
        id: 's-1',
        token: 'tok_abc',
        refreshToken: 'rtok_xyz',
        expiresAt: DateTime(2025, 6, 1),
        workspaceId: 'ws-1',
      );
      final json = model.toJson();
      final restored = SessionModel.fromJson(json);
      expect(restored.id, model.id);
      expect(restored.token, model.token);
      expect(restored.workspaceId, model.workspaceId);
    });

    test('UserModel roundtrip', () {
      final model = UserModel(
        id: 'u-1',
        email: 'test@jarvis.ai',
        displayName: 'Test User',
        avatarUrl: 'https://example.com/avatar.png',
        createdAt: DateTime(2025, 1, 1),
      );
      final json = model.toJson();
      final restored = UserModel.fromJson(json);
      expect(restored.email, model.email);
      expect(restored.displayName, model.displayName);
    });

    test('ConversationModel roundtrip', () {
      final model = ConversationModel(
        id: 'c-1',
        title: 'Test',
        projectId: 'p-1',
        workspaceId: 'ws-1',
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 2),
        messageCount: 3,
        isArchived: false,
      );
      final json = model.toJson();
      final restored = ConversationModel.fromJson(json);
      expect(restored.title, 'Test');
      expect(restored.messageCount, 3);
    });

    test('MessageModel roundtrip', () {
      final model = MessageModel(
        id: 'm-1',
        conversationId: 'c-1',
        role: 'user',
        content: 'Hello',
        createdAt: DateTime(2025, 1, 1),
      );
      final json = model.toJson();
      final restored = MessageModel.fromJson(json);
      expect(restored.role, 'user');
      expect(restored.content, 'Hello');
    });

    test('ProjectModel roundtrip', () {
      final model = ProjectModel(
        id: 'p-1',
        name: 'Project A',
        description: 'Desc',
        status: 'active',
        progress: 0.75,
        workspaceId: 'ws-1',
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 2),
      );
      final json = model.toJson();
      final restored = ProjectModel.fromJson(json);
      expect(restored.name, 'Project A');
      expect(restored.progress, 0.75);
    });

    test('WorkflowModel roundtrip', () {
      final model = WorkflowModel(
        id: 'w-1',
        name: 'Workflow A',
        description: 'Desc',
        status: 'running',
        trigger: 'schedule',
        lastRunAt: DateTime(2025, 1, 1),
        nextRunAt: DateTime(2025, 1, 2),
        createdAt: DateTime(2025, 1, 1),
      );
      final json = model.toJson();
      final restored = WorkflowModel.fromJson(json);
      expect(restored.name, 'Workflow A');
      expect(restored.status, 'running');
    });

    test('AppHealthModel roundtrip', () {
      final model = AppHealthModel(
        status: 'healthy',
        gatewayConnected: true,
        lastCheckedAt: DateTime(2025, 1, 1),
        version: '1.0.0',
      );
      final json = model.toJson();
      final restored = AppHealthModel.fromJson(json);
      expect(restored.status, 'healthy');
      expect(restored.gatewayConnected, true);
    });
  });
}
