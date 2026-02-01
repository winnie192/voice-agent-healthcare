import '../models/call_log.dart';
import 'api_client.dart';

class CallLogService {
  final ApiClient _client;

  CallLogService(this._client);

  Future<List<CallLogResponse>> listCallLogs(String businessId) async {
    final response =
        await _client.dio.get('/businesses/$businessId/call-logs');
    return (response.data as List<dynamic>)
        .map((e) => CallLogResponse.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
