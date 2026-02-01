import '../models/business.dart';
import 'api_client.dart';

class BusinessService {
  final ApiClient _client;

  BusinessService(this._client);

  Future<BusinessResponse> getBusiness(String businessId) async {
    final response = await _client.dio.get('/businesses/$businessId');
    return BusinessResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<BusinessResponse> updateBusiness(
      String businessId, BusinessUpdate update) async {
    final response = await _client.dio
        .patch('/businesses/$businessId', data: update.toJson());
    return BusinessResponse.fromJson(response.data as Map<String, dynamic>);
  }
}
