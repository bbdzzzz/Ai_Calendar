class Report {
  final int id;
  final String reportType;
  final DateTime startDate;
  final DateTime endDate;
  final String summary;
  final Map<String, dynamic>? statistics;
  final DateTime createdAt;

  Report({
    required this.id,
    required this.reportType,
    required this.startDate,
    required this.endDate,
    required this.summary,
    this.statistics,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory Report.fromJson(Map<String, dynamic> json) => Report(
        id: json['id'],
        reportType: json['report_type'],
        startDate: DateTime.parse(json['start_date']),
        endDate: DateTime.parse(json['end_date']),
        summary: json['summary'] ?? '',
        statistics: json['statistics'],
        createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      );
}
