import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../providers/auth_provider.dart';
import '../providers/bookings_provider.dart';
import '../providers/services_provider.dart';
import '../models/booking.dart';
import '../widgets/app_drawer.dart';

class BookingsScreen extends StatefulWidget {
  const BookingsScreen({super.key});

  @override
  State<BookingsScreen> createState() => _BookingsScreenState();
}

class _BookingsScreenState extends State<BookingsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final businessId = context.read<AuthProvider>().businessId;
    if (businessId == null) return;
    await Future.wait([
      context.read<BookingsProvider>().loadBookings(businessId),
      context.read<ServicesProvider>().loadServices(businessId),
    ]);
  }

  String _serviceName(String serviceId) {
    final services = context.read<ServicesProvider>().services;
    final match = services.where((s) => s.id == serviceId);
    return match.isNotEmpty ? match.first.name : 'Unknown Service';
  }

  String _formatDateTime(String isoString) {
    try {
      final dt = DateTime.parse(isoString).toLocal();
      return DateFormat('MMM d, yyyy  h:mm a').format(dt);
    } catch (_) {
      return isoString;
    }
  }

  Color _statusColor(String status) {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      case 'pending':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bookings = context.watch<BookingsProvider>().bookings;
    final loading = context.watch<BookingsProvider>().loading;

    return Scaffold(
      appBar: AppBar(title: const Text('Bookings')),
      drawer: const AppDrawer(),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : bookings.isEmpty
              ? const Center(child: Text('No bookings yet'))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: bookings.length,
                    itemBuilder: (context, index) {
                      final b = bookings[index];
                      return _BookingCard(
                        booking: b,
                        serviceName: _serviceName(b.serviceId),
                        formattedStart: _formatDateTime(b.startTime),
                        formattedEnd: _formatDateTime(b.endTime),
                        statusColor: _statusColor(b.status),
                      );
                    },
                  ),
                ),
    );
  }
}

class _BookingCard extends StatelessWidget {
  final BookingResponse booking;
  final String serviceName;
  final String formattedStart;
  final String formattedEnd;
  final Color statusColor;

  const _BookingCard({
    required this.booking,
    required this.serviceName,
    required this.formattedStart,
    required this.formattedEnd,
    required this.statusColor,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    serviceName,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                Chip(
                  label: Text(
                    booking.status.toUpperCase(),
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                  ),
                  backgroundColor: statusColor,
                  padding: EdgeInsets.zero,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ],
            ),
            const SizedBox(height: 8),
            _DetailRow(icon: Icons.person, text: booking.customerName),
            if (booking.customerPhone.isNotEmpty)
              _DetailRow(icon: Icons.phone, text: booking.customerPhone),
            _DetailRow(icon: Icons.access_time, text: formattedStart),
            _DetailRow(
              icon: Icons.timelapse,
              text: 'Until $formattedEnd',
            ),
            if (booking.notes != null && booking.notes!.isNotEmpty)
              _DetailRow(icon: Icons.notes, text: booking.notes!),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String text;

  const _DetailRow({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.grey),
          const SizedBox(width: 8),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}
