class BookingResponse {
  final String id;
  final String businessId;
  final String serviceId;
  final String customerName;
  final String customerPhone;
  final String startTime;
  final String endTime;
  final String status;
  final String? notes;
  final String createdAt;

  BookingResponse({
    required this.id,
    required this.businessId,
    required this.serviceId,
    required this.customerName,
    required this.customerPhone,
    required this.startTime,
    required this.endTime,
    required this.status,
    this.notes,
    required this.createdAt,
  });

  factory BookingResponse.fromJson(Map<String, dynamic> json) {
    return BookingResponse(
      id: json['id'] as String,
      businessId: json['business_id'] as String,
      serviceId: json['service_id'] as String,
      customerName: json['customer_name'] as String,
      customerPhone: json['customer_phone'] as String,
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
      status: json['status'] as String,
      notes: json['notes'] as String?,
      createdAt: json['created_at'] as String,
    );
  }
}
