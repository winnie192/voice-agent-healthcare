import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/call_logs_provider.dart';
import '../widgets/app_drawer.dart';

class CallLogsScreen extends StatefulWidget {
  const CallLogsScreen({super.key});

  @override
  State<CallLogsScreen> createState() => _CallLogsScreenState();
}

class _CallLogsScreenState extends State<CallLogsScreen> {
  @override
  void initState() {
    super.initState();
    final bid = context.read<AuthProvider>().businessId;
    if (bid != null) context.read<CallLogsProvider>().loadCallLogs(bid);
  }

  @override
  Widget build(BuildContext context) {
    final cp = context.watch<CallLogsProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Call Logs')),
      drawer: const AppDrawer(),
      body: cp.loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: cp.callLogs.length,
              itemBuilder: (_, i) {
                final log = cp.callLogs[i];
                return ListTile(
                  leading: const Icon(Icons.call),
                  title: Text(log.callerPhone ?? 'Unknown'),
                  subtitle: Text(
                      'Intent: ${log.intent ?? '-'} | Outcome: ${log.outcome ?? '-'}'),
                  trailing: log.durationSeconds != null
                      ? Text('${log.durationSeconds}s')
                      : null,
                );
              },
            ),
    );
  }
}
