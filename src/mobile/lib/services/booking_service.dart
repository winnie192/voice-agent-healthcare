import '../models/booking.dart';
import 'api_client.dart';

class BookingService {
  final ApiClient _client;

  BookingService(this._client);

  Future<List<BookingResponse>> listBookings(String businessId) async {
    final response =
        await _client.dio.get('/businesses/$businessId/bookings');
    return (response.data as List<dynamic>)
        .map((e) => BookingResponse.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
