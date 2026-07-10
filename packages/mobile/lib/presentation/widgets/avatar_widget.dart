import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:jarvis_mobile/core/extensions/context_extensions.dart';
import 'package:jarvis_mobile/core/theme/app_spacing.dart';

class AvatarWidget extends StatelessWidget {
  const AvatarWidget({
    super.key,
    this.imageUrl,
    required this.name,
    this.radius = 20,
    this.onTap,
  });

  final String? imageUrl;
  final String name;
  final double radius;
  final VoidCallback? onTap;

  String _initials() {
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
    }
    if (parts.length == 1 && parts.first.isNotEmpty) {
      return parts.first[0].toUpperCase();
    }
    return '?';
  }

  Color _color(String initials, ColorScheme scheme) {
    final hash = initials.codeUnits.fold<int>(0, (a, b) => a + b);
    final palette = [
      scheme.primary,
      scheme.secondary,
      scheme.tertiary,
      scheme.error,
      scheme.primaryContainer,
      scheme.secondaryContainer,
    ];
    return palette[hash % palette.length];
  }

  @override
  Widget build(BuildContext context) {
    final initials = _initials();
    final bgColor = _color(initials, context.colorScheme);

    return Semantics(
      button: onTap != null,
      label: name,
      image: imageUrl != null,
      child: GestureDetector(
        onTap: onTap,
        child: CircleAvatar(
          radius: radius,
          backgroundColor: bgColor.withValues(alpha: 0.2),
          backgroundImage: imageUrl != null ? CachedNetworkImageProvider(imageUrl!) : null,
          child: imageUrl == null
              ? Text(
                  initials,
                  style: TextStyle(
                    fontSize: radius * 0.6,
                    fontWeight: FontWeight.w600,
                    color: bgColor,
                  ),
                )
              : null,
        ),
      ),
    );
  }
}
