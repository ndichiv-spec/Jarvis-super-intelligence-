import 'package:flutter_test/flutter_test.dart';
import 'package:jarvis_mobile/domain/entities/app_health.dart';
import 'package:jarvis_mobile/domain/entities/app_settings.dart';
import 'package:jarvis_mobile/domain/entities/conversation.dart';
import 'package:jarvis_mobile/domain/entities/message.dart';
import 'package:jarvis_mobile/domain/entities/project.dart';
import 'package:jarvis_mobile/domain/entities/workflow.dart';
import 'package:jarvis_mobile/domain/entities/memory_item.dart';
import 'package:jarvis_mobile/domain/entities/notification.dart';
import 'package:jarvis_mobile/domain/entities/device.dart';

void main() {
  group('Entities', () {
    test('AppHealth', () {
      final health = AppHealth(
        status: HealthStatus.healthy,
        gatewayConnected: true,
        lastCheckedAt: DateTime(2025, 1, 1),
        version: '1.0.0',
      );
      expect(health.status, HealthStatus.healthy);
      expect(health.gatewayConnected, true);
      expect(health.version, '1.0.0');
    });

    test('AppSettings', () {
      final settings = AppSettings(
        themeMode: ThemeModeType.dark,
        locale: 'en',
        notificationsEnabled: true,
        biometricEnabled: false,
        offlineModeEnabled: true,
        workspaceId: 'ws-1',
      );
      expect(settings.themeMode, ThemeModeType.dark);
      expect(settings.locale, 'en');
      expect(settings.workspaceId, 'ws-1');
    });

    test('Conversation', () {
      final conversation = Conversation(
        id: 'conv-1',
        title: 'Test',
        workspaceId: 'ws-1',
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 2),
        messageCount: 5,
        isArchived: false,
      );
      expect(conversation.id, 'conv-1');
      expect(conversation.title, 'Test');
      expect(conversation.messageCount, 5);
    });

    test('Message', () {
      final message = Message(
        id: 'msg-1',
        conversationId: 'conv-1',
        role: MessageRole.user,
        content: 'Hello',
        createdAt: DateTime(2025, 1, 1),
      );
      expect(message.role, MessageRole.user);
      expect(message.content, 'Hello');
    });

    test('Project', () {
      final project = Project(
        id: 'proj-1',
        name: 'Test Project',
        description: 'A test',
        status: ProjectStatus.active,
        progress: 0.5,
        workspaceId: 'ws-1',
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 2),
      );
      expect(project.status, ProjectStatus.active);
      expect(project.progress, 0.5);
    });

    test('Workflow', () {
      final workflow = Workflow(
        id: 'wf-1',
        name: 'Test Workflow',
        description: 'A workflow',
        status: WorkflowStatus.running,
        trigger: 'manual',
        lastRunAt: DateTime(2025, 1, 1),
        createdAt: DateTime(2025, 1, 1),
      );
      expect(workflow.status, WorkflowStatus.running);
      expect(workflow.trigger, 'manual');
    });

    test('MemoryItem', () {
      final memory = MemoryItem(
        id: 'mem-1',
        content: 'Remember this',
        type: 'fact',
        source: 'conversation',
        importance: 'high',
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 2),
        isArchived: false,
      );
      expect(memory.type, 'fact');
      expect(memory.importance, 'high');
    });

    test('Notification', () {
      final notif = JarvisNotification(
        id: 'notif-1',
        type: 'workflow_completed',
        title: 'Done',
        body: 'Workflow finished',
        isRead: false,
        createdAt: DateTime(2025, 1, 1),
      );
      expect(notif.type, 'workflow_completed');
      expect(notif.isRead, false);
    });

    test('Device', () {
      final device = Device(
        id: 'dev-1',
        name: 'My Phone',
        type: 'phone',
        platform: 'iOS',
        lastSeenAt: DateTime(2025, 1, 1),
        isTrusted: true,
        isCurrentDevice: true,
      );
      expect(device.name, 'My Phone');
      expect(device.isTrusted, true);
    });
  });
}
