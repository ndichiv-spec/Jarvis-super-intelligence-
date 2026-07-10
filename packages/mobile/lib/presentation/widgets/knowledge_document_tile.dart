import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/extensions/date_time_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';
import 'package:jarvis_mobile/core/utils/formatters.dart';
import 'package:jarvis_mobile/domain/entities/knowledge_document.dart';

class KnowledgeDocumentTile extends StatelessWidget {
  const KnowledgeDocumentTile({
    super.key,
    required this.document,
    this.onTap,
  });

  final KnowledgeDocument document;
  final VoidCallback? onTap;

  IconData _iconForType(String type) {
    switch (type.toLowerCase()) {
      case 'pdf':
        return Icons.picture_as_pdf_rounded;
      case 'doc':
      case 'docx':
        return Icons.description_rounded;
      case 'text':
      case 'txt':
        return Icons.article_rounded;
      case 'markdown':
      case 'md':
        return Icons.code_rounded;
      case 'image':
      case 'png':
      case 'jpg':
      case 'jpeg':
        return Icons.image_rounded;
      case 'link':
      case 'url':
        return Icons.link_rounded;
      case 'code':
      case 'source':
        return Icons.terminal_rounded;
      case 'spreadsheet':
      case 'xlsx':
      case 'csv':
        return Icons.table_chart_rounded;
      default:
        return Icons.insert_drive_file_outlined;
    }
  }

  Color _colorForType(String type, ColorScheme scheme) {
    switch (type.toLowerCase()) {
      case 'pdf':
        return scheme.error;
      case 'doc':
      case 'docx':
        return scheme.primary;
      case 'image':
        return scheme.tertiary;
      case 'code':
      case 'source':
        return scheme.secondary;
      case 'link':
        return scheme.outline;
      default:
        return scheme.onSurfaceVariant;
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = context.colorScheme;
    final docColor = _colorForType(document.documentType, scheme);

    return Semantics(
      button: true,
      label: 'Document: ${document.title}',
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: docColor.withValues(alpha: 0.12),
          radius: 20,
          child: Icon(
            _iconForType(document.documentType),
            size: AppSpacing.iconSm,
            color: docColor,
          ),
        ),
        title: Text(
          document.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: context.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Row(
          children: [
            Text(
              document.documentType.toUpperCase(),
              style: context.textTheme.labelSmall?.copyWith(
                color: docColor,
                fontWeight: FontWeight.w600,
              ),
            ),
            if (document.fileSize != null) ...[
              const SizedBox(width: AppSpacing.sm),
              Text(
                '${ByteFormatter.format(document.fileSize!)} \u2022',
                style: context.textTheme.bodySmall?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(width: AppSpacing.xs),
            ],
            Text(
              document.createdAt.formatShort(),
              style: context.textTheme.bodySmall?.copyWith(
                color: scheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right_rounded),
        onTap: onTap,
      ),
    );
  }
}
