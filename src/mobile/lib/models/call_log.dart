class CallLogResponse {
  final String id;
  final String businessId;
  final String? callerPhone;
  final String? transcript;
  final String? intent;
  final String? outcome;
  final int? durationSeconds;
  final String createdAt;

  CallLogResponse({
    required this.id,
    required this.businessId,
    this.callerPhone,
    this.transcript,
    this.intent,
    this.outcome,
    this.durationSeconds,
    required this.createdAt,
  });

  factory CallLogResponse.fromJson(Map<String, dynamic> json) {
    return CallLogResponse(
      id: json['id'] as String,
      businessId: json['business_id'] as String,
      callerPhone: json['caller_phone'] as String?,
      transcript: json['transcript'] as String?,
      intent: json['intent'] as String?,
      outcome: json['outcome'] as String?,
      durationSeconds: json['duration_seconds'] as int?,
      createdAt: json['created_at'] as String,
    );
  }
}
