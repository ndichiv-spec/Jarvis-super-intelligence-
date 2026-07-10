import 'package:equatable/equatable.dart';

class QuickAction extends Equatable {
  final String id;
  final String label;
  final String iconName;
  final String actionType;
  final Map<String, dynamic>? actionPayload;
  final int order;
  final bool isEnabled;

  const QuickAction({
    required this.id,
    required this.label,
    required this.iconName,
    required this.actionType,
    this.actionPayload,
    required this.order,
    required this.isEnabled,
  });

  @override
  List<Object?> get props => [
        id,
        label,
        iconName,
        actionType,
        actionPayload,
        order,
        isEnabled,
      ];
}
