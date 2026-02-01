import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/business_provider.dart';
import '../providers/services_provider.dart';
import '../providers/bookings_provider.dart';
import '../providers/call_logs_provider.dart';
import '../widgets/app_drawer.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final businessId = context.read<AuthProvider>().businessId;
    if (businessId == null) return;
    await Future.wait([
      context.read<BusinessProvider>().loadBusiness(businessId),
      context.read<ServicesProvider>().loadServices(businessId),
      context.read<BookingsProvider>().loadBookings(businessId),
      context.read<CallLogsProvider>().loadCallLogs(businessId),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final business = context.watch<BusinessProvider>().business;
    final servicesCount = context.watch<ServicesProvider>().services.length;
    final bookingsCount = context.watch<BookingsProvider>().bookings.length;
    final callsCount = context.watch<CallLogsProvider>().callLogs.length;

    return Scaffold(
      appBar: AppBar(title: Text(business?.name ?? 'Dashboard')),
      drawer: const AppDrawer(),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _StatCard(label: 'Services', count: servicesCount, icon: Icons.medical_services, onTap: () => context.go('/services')),
            _StatCard(label: 'Bookings', count: bookingsCount, icon: Icons.calendar_today, onTap: () => context.go('/bookings')),
            _StatCard(label: 'Call Logs', count: callsCount, icon: Icons.call, onTap: () => context.go('/call-logs')),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final int count;
  final IconData icon;
  final VoidCallback? onTap;

  const _StatCard({required this.label, required this.count, required this.icon, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(icon, size: 36),
        title: Text(label),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('$count', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(width: 8),
            const Icon(Icons.chevron_right),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
}
