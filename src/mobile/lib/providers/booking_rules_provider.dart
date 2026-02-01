import 'package:flutter/foundation.dart';

import '../models/booking_rule.dart';
import '../services/booking_rule_service.dart';

class BookingRulesProvider extends ChangeNotifier {
  final BookingRuleService _service;

  BookingRuleResponse? _rules;
  bool _loading = false;
  String? _error;

  BookingRulesProvider(this._service);

  BookingRuleResponse? get rules => _rules;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadRules(String businessId) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _rules = await _service.getBookingRules(businessId);
    } catch (e) {
      _error = 'Failed to load booking rules';
    }
    _loading = false;
    notifyListeners();
  }

  Future<void> updateRules(String businessId, BookingRuleUpdate data) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _rules = await _service.updateBookingRules(businessId, data);
    } catch (e) {
      _error = 'Failed to update booking rules';
    }
    _loading = false;
    notifyListeners();
  }
}
