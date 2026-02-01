import '../models/booking_rule.dart';
import 'api_client.dart';

class BookingRuleService {
  final ApiClient _client;

  BookingRuleService(this._client);

  Future<BookingRuleResponse?> getBookingRules(String businessId) async {
    final response =
        await _client.dio.get('/businesses/$businessId/booking-rules');
    if (response.data == null) return null;
    return BookingRuleResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<BookingRuleResponse> updateBookingRules(
      String businessId, BookingRuleUpdate data) async {
    final response = await _client.dio
        .put('/businesses/$businessId/booking-rules', data: data.toJson());
    return BookingRuleResponse.fromJson(response.data as Map<String, dynamic>);
  }
}
