import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
            ),
            child: const Text(
              'Healthcare Voice Agent',
              style: TextStyle(color: Colors.white, fontSize: 20),
            ),
          ),
          _tile(context, 'Dashboard', Icons.dashboard, '/dashboard'),
          _tile(context, 'Settings', Icons.settings, '/settings'),
          _tile(context, 'Services', Icons.medical_services, '/services'),
          _tile(context, 'Booking Rules', Icons.rule, '/booking-rules'),
          _tile(context, 'Bookings', Icons.calendar_today, '/bookings'),
          _tile(context, 'Knowledge Base', Icons.library_books, '/knowledge-base'),
          _tile(context, 'Call Logs', Icons.call, '/call-logs'),
          _tile(context, 'Voice Call', Icons.mic, '/voice-call'),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Logout'),
            onTap: () async {
              await context.read<AuthProvider>().logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
    );
  }

  Widget _tile(BuildContext context, String title, IconData icon, String path) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      onTap: () {
        Navigator.pop(context);
        context.go(path);
      },
    );
  }
}
