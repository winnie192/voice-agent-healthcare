class BookingRuleUpdate {
  final int? advanceNoticeHours;
  final int? maxAdvanceDays;
  final int? cancellationHours;
  final List<String>? allowedDays;

  BookingRuleUpdate({
    this.advanceNoticeHours,
    this.maxAdvanceDays,
    this.cancellationHours,
    this.allowedDays,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (advanceNoticeHours != null) map['advance_notice_hours'] = advanceNoticeHours;
    if (maxAdvanceDays != null) map['max_advance_days'] = maxAdvanceDays;
    if (cancellationHours != null) map['cancellation_hours'] = cancellationHours;
    if (allowedDays != null) map['allowed_days'] = allowedDays;
    return map;
  }
}

class BookingRuleResponse {
  final String id;
  final String businessId;
  final int advanceNoticeHours;
  final int maxAdvanceDays;
  final int cancellationHours;
  final List<String>? allowedDays;
  final String createdAt;

  BookingRuleResponse({
    required this.id,
    required this.businessId,
    required this.advanceNoticeHours,
    required this.maxAdvanceDays,
    required this.cancellationHours,
    this.allowedDays,
    required this.createdAt,
  });

  factory BookingRuleResponse.fromJson(Map<String, dynamic> json) {
    return BookingRuleResponse(
      id: json['id'] as String,
      businessId: json['business_id'] as String,
      advanceNoticeHours: json['advance_notice_hours'] as int,
      maxAdvanceDays: json['max_advance_days'] as int,
      cancellationHours: json['cancellation_hours'] as int,
      allowedDays: (json['allowed_days'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      createdAt: json['created_at'] as String,
    );
  }
}
