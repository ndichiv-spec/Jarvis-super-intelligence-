import 'package:equatable/equatable.dart';

class Attachment extends Equatable {
  final String id;
  final String name;
  final String type;
  final int size;
  final String url;
  final String? mimeType;

  const Attachment({
    required this.id,
    required this.name,
    required this.type,
    required this.size,
    required this.url,
    this.mimeType,
  });

  @override
  List<Object?> get props => [id, name, type, size, url, mimeType];
}
