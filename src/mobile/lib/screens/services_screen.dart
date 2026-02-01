import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/service.dart';
import '../providers/auth_provider.dart';
import '../providers/services_provider.dart';
import '../widgets/app_drawer.dart';

class ServicesScreen extends StatefulWidget {
  const ServicesScreen({super.key});

  @override
  State<ServicesScreen> createState() => _ServicesScreenState();
}

class _ServicesScreenState extends State<ServicesScreen> {
  @override
  void initState() {
    super.initState();
    final bid = context.read<AuthProvider>().businessId;
    if (bid != null) context.read<ServicesProvider>().loadServices(bid);
  }

  Future<void> _showForm({ServiceResponse? existing}) async {
    final nameCtrl = TextEditingController(text: existing?.name ?? '');
    final descCtrl = TextEditingController(text: existing?.description ?? '');
    final durCtrl = TextEditingController(
        text: existing?.durationMinutes.toString() ?? '');
    final priceCtrl =
        TextEditingController(text: existing?.price?.toString() ?? '');

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(existing == null ? 'Add Service' : 'Edit Service'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(labelText: 'Name')),
              TextField(
                  controller: descCtrl,
                  decoration: const InputDecoration(labelText: 'Description')),
              TextField(
                  controller: durCtrl,
                  decoration:
                      const InputDecoration(labelText: 'Duration (minutes)'),
                  keyboardType: TextInputType.number),
              TextField(
                  controller: priceCtrl,
                  decoration: const InputDecoration(labelText: 'Price'),
                  keyboardType: TextInputType.number),
            ],
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Save')),
        ],
      ),
    );

    if (result != true || !mounted) return;
    final bid = context.read<AuthProvider>().businessId!;
    final sp = context.read<ServicesProvider>();

    if (existing == null) {
      await sp.createService(
          bid,
          ServiceCreate(
            name: nameCtrl.text,
            description: descCtrl.text.isEmpty ? null : descCtrl.text,
            durationMinutes: int.tryParse(durCtrl.text) ?? 30,
            price: double.tryParse(priceCtrl.text),
          ));
    } else {
      await sp.updateService(
          bid,
          existing.id,
          ServiceUpdate(
            name: nameCtrl.text,
            description: descCtrl.text.isEmpty ? null : descCtrl.text,
            durationMinutes: int.tryParse(durCtrl.text),
            price: double.tryParse(priceCtrl.text),
          ));
    }
  }

  Future<void> _delete(String serviceId) async {
    final bid = context.read<AuthProvider>().businessId!;
    await context.read<ServicesProvider>().deleteService(bid, serviceId);
  }

  @override
  Widget build(BuildContext context) {
    final sp = context.watch<ServicesProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Services')),
      drawer: const AppDrawer(),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showForm(),
        child: const Icon(Icons.add),
      ),
      body: sp.loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: sp.services.length,
              itemBuilder: (_, i) {
                final s = sp.services[i];
                return ListTile(
                  title: Text(s.name),
                  subtitle: Text(
                      '${s.durationMinutes} min${s.price != null ? ' - \$${s.price!.toStringAsFixed(2)}' : ''}'),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                          icon: const Icon(Icons.edit),
                          onPressed: () => _showForm(existing: s)),
                      IconButton(
                          icon: const Icon(Icons.delete),
                          onPressed: () => _delete(s.id)),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
