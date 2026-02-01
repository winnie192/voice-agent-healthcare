import 'package:flutter/foundation.dart';

import '../models/service.dart';
import '../services/service_service.dart';

class ServicesProvider extends ChangeNotifier {
  final ServiceService _service;

  List<ServiceResponse> _services = [];
  bool _loading = false;
  String? _error;

  ServicesProvider(this._service);

  List<ServiceResponse> get services => _services;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadServices(String businessId) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _services = await _service.listServices(businessId);
    } catch (e) {
      _error = 'Failed to load services';
    }
    _loading = false;
    notifyListeners();
  }

  Future<void> createService(String businessId, ServiceCreate data) async {
    try {
      await _service.createService(businessId, data);
      await loadServices(businessId);
    } catch (e) {
      _error = 'Failed to create service';
      notifyListeners();
    }
  }

  Future<void> updateService(
      String businessId, String serviceId, ServiceUpdate data) async {
    try {
      await _service.updateService(businessId, serviceId, data);
      await loadServices(businessId);
    } catch (e) {
      _error = 'Failed to update service';
      notifyListeners();
    }
  }

  Future<void> deleteService(String businessId, String serviceId) async {
    try {
      await _service.deleteService(businessId, serviceId);
      await loadServices(businessId);
    } catch (e) {
      _error = 'Failed to delete service';
      notifyListeners();
    }
  }
}
