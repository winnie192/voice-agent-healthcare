import '../models/auth.dart';
import '../models/business.dart';
import 'api_client.dart';

class AuthService {
  final ApiClient _client;

  AuthService(this._client);

  Future<TokenResponse> login(LoginRequest request) async {
    final response = await _client.dio.post('/auth/login', data: request.toJson());
    final token = TokenResponse.fromJson(response.data as Map<String, dynamic>);
    await _client.saveToken(token.accessToken);
    return token;
  }

  Future<BusinessResponse> register(BusinessCreate request) async {
    final response =
        await _client.dio.post('/businesses', data: request.toJson());
    return BusinessResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await _client.clearToken();
  }
}
