import '../models/document.dart';
import 'api_client.dart';

class KnowledgeBaseService {
  final ApiClient _client;

  KnowledgeBaseService(this._client);

  Future<List<DocumentResponse>> listDocuments(String businessId) async {
    final response =
        await _client.dio.get('/businesses/$businessId/knowledge-base');
    return (response.data as List<dynamic>)
        .map((e) => DocumentResponse.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<DocumentResponse> createDocument(
      String businessId, DocumentCreate data) async {
    final response = await _client.dio
        .post('/businesses/$businessId/knowledge-base', data: data.toJson());
    return DocumentResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteDocument(String businessId, String docId) async {
    await _client.dio
        .delete('/businesses/$businessId/knowledge-base/$docId');
  }
}
