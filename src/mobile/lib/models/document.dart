class DocumentCreate {
  final String title;
  final String content;

  DocumentCreate({required this.title, required this.content});

  Map<String, dynamic> toJson() => {'title': title, 'content': content};
}

class DocumentResponse {
  final String id;
  final String businessId;
  final String title;
  final String content;
  final String createdAt;

  DocumentResponse({
    required this.id,
    required this.businessId,
    required this.title,
    required this.content,
    required this.createdAt,
  });

  factory DocumentResponse.fromJson(Map<String, dynamic> json) {
    return DocumentResponse(
      id: json['id'] as String,
      businessId: json['business_id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      createdAt: json['created_at'] as String,
    );
  }
}
