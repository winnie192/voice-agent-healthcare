import 'package:flutter/foundation.dart';

import '../models/business.dart';
import '../services/business_service.dart';

class BusinessProvider extends ChangeNotifier {
  final BusinessService _service;

  BusinessResponse? _business;
  bool _loading = false;
  String? _error;

  BusinessProvider(this._service);

  BusinessResponse? get business => _business;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadBusiness(String businessId) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _business = await _service.getBusiness(businessId);
    } catch (e) {
      _error = 'Failed to load business';
    }
    _loading = false;
    notifyListeners();
  }

  Future<void> updateBusiness(String businessId, BusinessUpdate update) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _business = await _service.updateBusiness(businessId, update);
    } catch (e) {
      _error = 'Failed to update business';
    }
    _loading = false;
    notifyListeners();
  }
}
