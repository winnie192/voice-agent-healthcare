import '../models/service.dart';
import 'api_client.dart';

class ServiceService {
  final ApiClient _client;

  ServiceService(this._client);

  Future<List<ServiceResponse>> listServices(String businessId) async {
    final response =
        await _client.dio.get('/businesses/$businessId/services');
    return (response.data as List<dynamic>)
        .map((e) => ServiceResponse.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<ServiceResponse> createService(
      String businessId, ServiceCreate data) async {
    final response = await _client.dio
        .post('/businesses/$businessId/services', data: data.toJson());
    return ServiceResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ServiceResponse> updateService(
      String businessId, String serviceId, ServiceUpdate data) async {
    final response = await _client.dio
        .patch('/businesses/$businessId/services/$serviceId', data: data.toJson());
    return ServiceResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteService(String businessId, String serviceId) async {
    await _client.dio.delete('/businesses/$businessId/services/$serviceId');
  }
}
