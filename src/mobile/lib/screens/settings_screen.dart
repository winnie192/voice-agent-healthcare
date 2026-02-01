import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/business.dart';
import '../providers/auth_provider.dart';
import '../providers/business_provider.dart';
import '../widgets/app_drawer.dart';
import '../widgets/loading_overlay.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _timezoneCtrl = TextEditingController();
  final _locationCtrl = TextEditingController();
  final _policiesCtrl = TextEditingController();
  bool _initialized = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _phoneCtrl.dispose();
    _timezoneCtrl.dispose();
    _locationCtrl.dispose();
    _policiesCtrl.dispose();
    super.dispose();
  }

  void _populateFields(BusinessResponse b) {
    if (_initialized) return;
    _initialized = true;
    _nameCtrl.text = b.name;
    _phoneCtrl.text = b.phone;
    _timezoneCtrl.text = b.timezone;
    _locationCtrl.text = b.location ?? '';
    _policiesCtrl.text = b.policies ?? '';
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    final businessId = context.read<AuthProvider>().businessId!;
    await context.read<BusinessProvider>().updateBusiness(
          businessId,
          BusinessUpdate(
            name: _nameCtrl.text,
            phone: _phoneCtrl.text,
            timezone: _timezoneCtrl.text,
            location: _locationCtrl.text.isEmpty ? null : _locationCtrl.text,
            policies: _policiesCtrl.text.isEmpty ? null : _policiesCtrl.text,
          ),
        );
    if (mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Settings saved')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final bp = context.watch<BusinessProvider>();
    if (bp.business != null) _populateFields(bp.business!);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      drawer: const AppDrawer(),
      body: LoadingOverlay(
        loading: bp.loading,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                TextFormField(
                  controller: _nameCtrl,
                  decoration: const InputDecoration(labelText: 'Business Name'),
                  validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _phoneCtrl,
                  decoration: const InputDecoration(labelText: 'Phone'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _timezoneCtrl,
                  decoration: const InputDecoration(labelText: 'Timezone'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _locationCtrl,
                  decoration: const InputDecoration(labelText: 'Location'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _policiesCtrl,
                  decoration: const InputDecoration(labelText: 'Policies'),
                  maxLines: 4,
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: _save,
                    child: const Text('Save'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
