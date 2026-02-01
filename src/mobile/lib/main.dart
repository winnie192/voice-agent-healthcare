import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app.dart';
import 'services/api_client.dart';
import 'services/auth_service.dart';
import 'services/business_service.dart';
import 'services/service_service.dart';
import 'services/booking_rule_service.dart';
import 'services/booking_service.dart';
import 'services/knowledge_base_service.dart';
import 'services/call_log_service.dart';
import 'providers/auth_provider.dart';
import 'providers/business_provider.dart';
import 'providers/services_provider.dart';
import 'providers/booking_rules_provider.dart';
import 'providers/bookings_provider.dart';
import 'providers/knowledge_base_provider.dart';
import 'providers/call_logs_provider.dart';

void main() {
  final apiClient = ApiClient();
  final authService = AuthService(apiClient);
  final businessService = BusinessService(apiClient);
  final serviceService = ServiceService(apiClient);
  final bookingRuleService = BookingRuleService(apiClient);
  final bookingService = BookingService(apiClient);
  final knowledgeBaseService = KnowledgeBaseService(apiClient);
  final callLogService = CallLogService(apiClient);

  final authProvider = AuthProvider(authService, apiClient);
  authProvider.checkAuth();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider),
        ChangeNotifierProvider(create: (_) => BusinessProvider(businessService)),
        ChangeNotifierProvider(create: (_) => ServicesProvider(serviceService)),
        ChangeNotifierProvider(
            create: (_) => BookingRulesProvider(bookingRuleService)),
        ChangeNotifierProvider(create: (_) => BookingsProvider(bookingService)),
        ChangeNotifierProvider(
            create: (_) => KnowledgeBaseProvider(knowledgeBaseService)),
        ChangeNotifierProvider(create: (_) => CallLogsProvider(callLogService)),
      ],
      child: const App(),
    ),
  );
}
