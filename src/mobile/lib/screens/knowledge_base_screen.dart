import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/document.dart';
import '../providers/auth_provider.dart';
import '../providers/knowledge_base_provider.dart';
import '../widgets/app_drawer.dart';

class KnowledgeBaseScreen extends StatefulWidget {
  const KnowledgeBaseScreen({super.key});

  @override
  State<KnowledgeBaseScreen> createState() => _KnowledgeBaseScreenState();
}

class _KnowledgeBaseScreenState extends State<KnowledgeBaseScreen> {
  @override
  void initState() {
    super.initState();
    final bid = context.read<AuthProvider>().businessId;
    if (bid != null) {
      context.read<KnowledgeBaseProvider>().loadDocuments(bid);
    }
  }

  Future<void> _addDocument() async {
    final titleCtrl = TextEditingController();
    final contentCtrl = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Document'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                  controller: titleCtrl,
                  decoration: const InputDecoration(labelText: 'Title')),
              const SizedBox(height: 8),
              TextField(
                  controller: contentCtrl,
                  decoration: const InputDecoration(labelText: 'Content'),
                  maxLines: 5),
            ],
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Add')),
        ],
      ),
    );

    if (result != true || !mounted) return;
    final bid = context.read<AuthProvider>().businessId!;
    await context.read<KnowledgeBaseProvider>().createDocument(
        bid, DocumentCreate(title: titleCtrl.text, content: contentCtrl.text));
  }

  Future<void> _delete(String docId) async {
    final bid = context.read<AuthProvider>().businessId!;
    await context.read<KnowledgeBaseProvider>().deleteDocument(bid, docId);
  }

  @override
  Widget build(BuildContext context) {
    final kp = context.watch<KnowledgeBaseProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Knowledge Base')),
      drawer: const AppDrawer(),
      floatingActionButton: FloatingActionButton(
        onPressed: _addDocument,
        child: const Icon(Icons.add),
      ),
      body: kp.loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: kp.documents.length,
              itemBuilder: (_, i) {
                final d = kp.documents[i];
                return ListTile(
                  title: Text(d.title),
                  subtitle: Text(d.content,
                      maxLines: 2, overflow: TextOverflow.ellipsis),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () => _delete(d.id),
                  ),
                );
              },
            ),
    );
  }
}
