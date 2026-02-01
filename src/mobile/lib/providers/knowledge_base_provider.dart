import 'package:flutter/foundation.dart';

import '../models/document.dart';
import '../services/knowledge_base_service.dart';

class KnowledgeBaseProvider extends ChangeNotifier {
  final KnowledgeBaseService _service;

  List<DocumentResponse> _documents = [];
  bool _loading = false;
  String? _error;

  KnowledgeBaseProvider(this._service);

  List<DocumentResponse> get documents => _documents;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadDocuments(String businessId) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _documents = await _service.listDocuments(businessId);
    } catch (e) {
      _error = 'Failed to load documents';
    }
    _loading = false;
    notifyListeners();
  }

  Future<void> createDocument(String businessId, DocumentCreate data) async {
    try {
      await _service.createDocument(businessId, data);
      await loadDocuments(businessId);
    } catch (e) {
      _error = 'Failed to create document';
      notifyListeners();
    }
  }

  Future<void> deleteDocument(String businessId, String docId) async {
    try {
      await _service.deleteDocument(businessId, docId);
      await loadDocuments(businessId);
    } catch (e) {
      _error = 'Failed to delete document';
      notifyListeners();
    }
  }
}
