import 'package:flutter/foundation.dart';

import '../models/booking.dart';
import '../services/booking_service.dart';

class BookingsProvider extends ChangeNotifier {
  final BookingService _service;

  List<BookingResponse> _bookings = [];
  bool _loading = false;
  String? _error;

  BookingsProvider(this._service);

  List<BookingResponse> get bookings => _bookings;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadBookings(String businessId) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _bookings = await _service.listBookings(businessId);
    } catch (e) {
      _error = 'Failed to load bookings';
    }
    _loading = false;
    notifyListeners();
  }
}
