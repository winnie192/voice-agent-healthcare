import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/booking_rule.dart';
import '../providers/auth_provider.dart';
import '../providers/booking_rules_provider.dart';
import '../widgets/app_drawer.dart';
import '../widgets/loading_overlay.dart';

class BookingRulesScreen extends StatefulWidget {
  const BookingRulesScreen({super.key});

  @override
  State<BookingRulesScreen> createState() => _BookingRulesScreenState();
}

class _BookingRulesScreenState extends State<BookingRulesScreen> {
  final _advanceCtrl = TextEditingController();
  final _maxDaysCtrl = TextEditingController();
  final _cancelCtrl = TextEditingController();
  bool _initialized = false;

  @override
  void initState() {
    super.initState();
    final bid = context.read<AuthProvider>().businessId;
    if (bid != null) context.read<BookingRulesProvider>().loadRules(bid);
  }

  @override
  void dispose() {
    _advanceCtrl.dispose();
    _maxDaysCtrl.dispose();
    _cancelCtrl.dispose();
    super.dispose();
  }

  void _populate(BookingRuleResponse r) {
    if (_initialized) return;
    _initialized = true;
    _advanceCtrl.text = r.advanceNoticeHours.toString();
    _maxDaysCtrl.text = r.maxAdvanceDays.toString();
    _cancelCtrl.text = r.cancellationHours.toString();
  }

  Future<void> _save() async {
    final bid = context.read<AuthProvider>().businessId!;
    await context.read<BookingRulesProvider>().updateRules(
          bid,
          BookingRuleUpdate(
            advanceNoticeHours: int.tryParse(_advanceCtrl.text),
            maxAdvanceDays: int.tryParse(_maxDaysCtrl.text),
            cancellationHours: int.tryParse(_cancelCtrl.text),
          ),
        );
    if (mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Rules saved')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final bp = context.watch<BookingRulesProvider>();
    if (bp.rules != null) _populate(bp.rules!);

    return Scaffold(
      appBar: AppBar(title: const Text('Booking Rules')),
      drawer: const AppDrawer(),
      body: LoadingOverlay(
        loading: bp.loading,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              TextField(
                controller: _advanceCtrl,
                decoration:
                    const InputDecoration(labelText: 'Advance Notice (hours)'),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _maxDaysCtrl,
                decoration:
                    const InputDecoration(labelText: 'Max Advance Days'),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _cancelCtrl,
                decoration:
                    const InputDecoration(labelText: 'Cancellation (hours)'),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: _save,
                  child: const Text('Save Rules'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
