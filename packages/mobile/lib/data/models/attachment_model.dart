import 'package:jarvis_mobile/domain/entities/attachment.dart';

class AttachmentModel {
  final String id;
  final String name;
  final String type;
  final int size;
  final String url;
  final String? mimeType;

  const AttachmentModel({
    required this.id,
    required this.name,
    required this.type,
    required this.size,
    required this.url,
    this.mimeType,
  });

  factory AttachmentModel.fromJson(Map<String, dynamic> json) {
    return AttachmentModel(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      size: json['size'] as int,
      url: json['url'] as String,
      mimeType: json['mimeType'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'size': size,
      'url': url,
      'mimeType': mimeType,
    };
  }

  Attachment toEntity() {
    return Attachment(
      id: id,
      name: name,
      type: type,
      size: size,
      url: url,
      mimeType: mimeType,
    );
  }

  factory AttachmentModel.fromEntity(Attachment entity) {
    return AttachmentModel(
      id: entity.id,
      name: entity.name,
      type: entity.type,
      size: entity.size,
      url: entity.url,
      mimeType: entity.mimeType,
    );
  }
}
