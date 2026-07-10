import 'package:equatable/equatable.dart';

class Workspace extends Equatable {
  final String id;
  final String name;
  final String? description;
  final String role;
  final int memberCount;

  const Workspace({
    required this.id,
    required this.name,
    this.description,
    required this.role,
    required this.memberCount,
  });

  @override
  List<Object?> get props => [id, name, description, role, memberCount];
}
