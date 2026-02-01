class BusinessCreate {
  final String name;
  final String phone;
  final String timezone;
  final String? location;
  final Map<String, dynamic>? hours;
  final String? policies;
  final String adminEmail;
  final String adminPassword;

  BusinessCreate({
    required this.name,
    required this.phone,
    this.timezone = 'UTC',
    this.location,
    this.hours,
    this.policies,
    required this.adminEmail,
    required this.adminPassword,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'phone': phone,
        'timezone': timezone,
        'location': location,
        'hours': hours,
        'policies': policies,
        'admin_email': adminEmail,
        'admin_password': adminPassword,
      };
}

class BusinessUpdate {
  final String? name;
  final String? phone;
  final String? timezone;
  final String? location;
  final Map<String, dynamic>? hours;
  final String? policies;

  BusinessUpdate({
    this.name,
    this.phone,
    this.timezone,
    this.location,
    this.hours,
    this.policies,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (name != null) map['name'] = name;
    if (phone != null) map['phone'] = phone;
    if (timezone != null) map['timezone'] = timezone;
    if (location != null) map['location'] = location;
    if (hours != null) map['hours'] = hours;
    if (policies != null) map['policies'] = policies;
    return map;
  }
}

class BusinessResponse {
  final String id;
  final String name;
  final String phone;
  final String timezone;
  final String? location;
  final Map<String, dynamic>? hours;
  final String? policies;
  final String createdAt;

  BusinessResponse({
    required this.id,
    required this.name,
    required this.phone,
    required this.timezone,
    this.location,
    this.hours,
    this.policies,
    required this.createdAt,
  });

  factory BusinessResponse.fromJson(Map<String, dynamic> json) {
    return BusinessResponse(
      id: json['id'] as String,
      name: json['name'] as String,
      phone: json['phone'] as String,
      timezone: json['timezone'] as String,
      location: json['location'] as String?,
      hours: json['hours'] as Map<String, dynamic>?,
      policies: json['policies'] as String?,
      createdAt: json['created_at'] as String,
    );
  }
}
