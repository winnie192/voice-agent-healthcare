import 'package:flutter/foundation.dart';

import '../models/call_log.dart';
import '../services/call_log_service.dart';

class CallLogsProvider extends ChangeNotifier {
  final CallLogService _service;

  List<CallLogResponse> _callLogs = [];
  bool _loading = false;
  String? _error;

  CallLogsProvider(this._service);

  List<CallLogResponse> get callLogs => _callLogs;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadCallLogs(String businessId) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _callLogs = await _service.listCallLogs(businessId);
    } catch (e) {
      _error = 'Failed to load call logs';
    }
    _loading = false;
    notifyListeners();
  }
}
