class ServiceCreate {
  final String name;
  final String? description;
  final int durationMinutes;
  final double? price;

  ServiceCreate({
    required this.name,
    this.description,
    required this.durationMinutes,
    this.price,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'description': description,
        'duration_minutes': durationMinutes,
        'price': price,
      };
}

class ServiceUpdate {
  final String? name;
  final String? description;
  final int? durationMinutes;
  final double? price;

  ServiceUpdate({this.name, this.description, this.durationMinutes, this.price});

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (name != null) map['name'] = name;
    if (description != null) map['description'] = description;
    if (durationMinutes != null) map['duration_minutes'] = durationMinutes;
    if (price != null) map['price'] = price;
    return map;
  }
}

class ServiceResponse {
  final String id;
  final String businessId;
  final String name;
  final String? description;
  final int durationMinutes;
  final double? price;
  final String createdAt;

  ServiceResponse({
    required this.id,
    required this.businessId,
    required this.name,
    this.description,
    required this.durationMinutes,
    this.price,
    required this.createdAt,
  });

  factory ServiceResponse.fromJson(Map<String, dynamic> json) {
    return ServiceResponse(
      id: json['id'] as String,
      businessId: json['business_id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      durationMinutes: json['duration_minutes'] as int,
      price: (json['price'] as num?)?.toDouble(),
      createdAt: json['created_at'] as String,
    );
  }
}
