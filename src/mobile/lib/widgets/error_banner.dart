import 'package:flutter/material.dart';

class ErrorBanner extends StatelessWidget {
  final String? message;

  const ErrorBanner({super.key, this.message});

  @override
  Widget build(BuildContext context) {
    if (message == null) return const SizedBox.shrink();
    return MaterialBanner(
      content: Text(message!),
      backgroundColor: Theme.of(context).colorScheme.errorContainer,
      actions: [
        TextButton(
          onPressed: () => ScaffoldMessenger.of(context).clearMaterialBanners(),
          child: const Text('DISMISS'),
        ),
      ],
    );
  }
}
