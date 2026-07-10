import 'package:jarvis_mobile/domain/entities/quick_action.dart';

class QuickActionModel {
  final String id;
  final String label;
  final String iconName;
  final String actionType;
  final Map<String, dynamic>? actionPayload;
  final int order;
  final bool isEnabled;

  const QuickActionModel({
    required this.id,
    required this.label,
    required this.iconName,
    required this.actionType,
    this.actionPayload,
    required this.order,
    required this.isEnabled,
  });

  factory QuickActionModel.fromJson(Map<String, dynamic> json) {
    return QuickActionModel(
      id: json['id'] as String,
      label: json['label'] as String,
      iconName: json['iconName'] as String,
      actionType: json['actionType'] as String,
      actionPayload: json['actionPayload'] as Map<String, dynamic>?,
      order: json['order'] as int,
      isEnabled: json['isEnabled'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'label': label,
      'iconName': iconName,
      'actionType': actionType,
      'actionPayload': actionPayload,
      'order': order,
      'isEnabled': isEnabled,
    };
  }

  QuickAction toEntity() {
    return QuickAction(
      id: id,
      label: label,
      iconName: iconName,
      actionType: actionType,
      actionPayload: actionPayload,
      order: order,
      isEnabled: isEnabled,
    );
  }

  factory QuickActionModel.fromEntity(QuickAction entity) {
    return QuickActionModel(
      id: entity.id,
      label: entity.label,
      iconName: entity.iconName,
      actionType: entity.actionType,
      actionPayload: entity.actionPayload,
      order: entity.order,
      isEnabled: entity.isEnabled,
    );
  }
}
