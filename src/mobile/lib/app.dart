import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/services_screen.dart';
import 'screens/booking_rules_screen.dart';
import 'screens/knowledge_base_screen.dart';
import 'screens/call_logs_screen.dart';
import 'screens/bookings_screen.dart';
import 'screens/voice_call_screen.dart';

GoRouter buildRouter(AuthProvider auth) {
  return GoRouter(
    refreshListenable: auth,
    initialLocation: '/login',
    redirect: (context, state) {
      final loggedIn = auth.isAuthenticated;
      final onAuth = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';

      if (!loggedIn && !onAuth) return '/login';
      if (loggedIn && onAuth) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
      GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
      GoRoute(path: '/services', builder: (_, __) => const ServicesScreen()),
      GoRoute(
          path: '/booking-rules',
          builder: (_, __) => const BookingRulesScreen()),
      GoRoute(
          path: '/knowledge-base',
          builder: (_, __) => const KnowledgeBaseScreen()),
      GoRoute(path: '/bookings', builder: (_, __) => const BookingsScreen()),
      GoRoute(path: '/call-logs', builder: (_, __) => const CallLogsScreen()),
      GoRoute(
          path: '/voice-call', builder: (_, __) => const VoiceCallScreen()),
    ],
  );
}

class App extends StatefulWidget {
  const App({super.key});

  @override
  State<App> createState() => _AppState();
}

class _AppState extends State<App> {
  GoRouter? _router;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _router ??= buildRouter(context.read<AuthProvider>());
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Healthcare Voice Agent',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.teal,
        useMaterial3: true,
        brightness: Brightness.light,
      ),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.teal,
        useMaterial3: true,
        brightness: Brightness.dark,
      ),
      routerConfig: _router!,
    );
  }
}
