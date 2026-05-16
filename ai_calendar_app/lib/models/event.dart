class CalendarEvent {
  final int? id;
  final String title;
  final String? description;
  final DateTime startTime;
  final DateTime endTime;
  final String? location;
  final String category;
  final String priority;
  final String status;
  final String source;

  CalendarEvent({
    this.id,
    required this.title,
    this.description,
    required this.startTime,
    required this.endTime,
    this.location,
    this.category = 'other',
    this.priority = 'medium',
    this.status = 'confirmed',
    this.source = 'manual',
  });

  factory CalendarEvent.fromJson(Map<String, dynamic> json) => CalendarEvent(
        id: json['id'],
        title: json['title'] ?? '',
        description: json['description'],
        startTime: DateTime.parse(json['start_time']),
        endTime: DateTime.parse(json['end_time']),
        location: json['location'],
        category: json['category'] ?? 'other',
        priority: json['priority'] ?? 'medium',
        status: json['status'] ?? 'confirmed',
        source: json['source'] ?? 'manual',
      );

  Map<String, dynamic> toJson() => {
        if (id != null) 'id': id,
        'title': title,
        if (description != null) 'description': description,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
        if (location != null) 'location': location,
        'category': category,
        'priority': priority,
        'status': status,
        'source': source,
      };

  CalendarEvent copyWith({
    int? id,
    String? title,
    String? description,
    DateTime? startTime,
    DateTime? endTime,
    String? location,
    String? category,
    String? priority,
    String? status,
    String? source,
  }) =>
      CalendarEvent(
        id: id ?? this.id,
        title: title ?? this.title,
        description: description ?? this.description,
        startTime: startTime ?? this.startTime,
        endTime: endTime ?? this.endTime,
        location: location ?? this.location,
        category: category ?? this.category,
        priority: priority ?? this.priority,
        status: status ?? this.status,
        source: source ?? this.source,
      );
}
