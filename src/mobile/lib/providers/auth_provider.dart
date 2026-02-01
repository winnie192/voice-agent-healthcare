import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../models/auth.dart';
import '../models/business.dart';
import '../services/auth_service.dart';
import '../services/api_client.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService;
  final ApiClient _apiClient;

  bool _isAuthenticated = false;
  String? _businessId;
  String? _error;
  bool _loading = false;

  AuthProvider(this._authService, this._apiClient);

  bool get isAuthenticated => _isAuthenticated;
  String? get businessId => _businessId;
  String? get error => _error;
  bool get loading => _loading;

  Future<void> checkAuth() async {
    final token = await _apiClient.getToken();
    if (token != null) {
      try {
        final parts = token.split('.');
        if (parts.length == 3) {
          final payload =
              jsonDecode(utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))))
                  as Map<String, dynamic>;
          _businessId = payload['business_id'] as String?;
          _isAuthenticated = true;
        }
      } catch (_) {
        await _apiClient.clearToken();
      }
    }
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      final token =
          await _authService.login(LoginRequest(email: email, password: password));
      final parts = token.accessToken.split('.');
      final payload =
          jsonDecode(utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))))
              as Map<String, dynamic>;
      _businessId = payload['business_id'] as String?;
      _isAuthenticated = true;
      _loading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = 'Login failed: $e';
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(BusinessCreate data) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _authService.register(data);
      _loading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = 'Registration failed. Please try again.';
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    _businessId = null;
    notifyListeners();
  }
}
