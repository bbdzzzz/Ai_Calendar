import 'package:flutter_test/flutter_test.dart';
import 'package:ai_calendar_app/models/user.dart';
import 'package:ai_calendar_app/models/event.dart';
import 'package:ai_calendar_app/models/conversation.dart';
import 'package:ai_calendar_app/models/report.dart';

void main() {
  group('AppUser', () {
    test('fromJson creates correct object', () {
      final json = {'id': 1, 'username': 'test', 'preferences': {'lang': 'zh'}};
      final user = AppUser.fromJson(json);
      expect(user.id, 1);
      expect(user.username, 'test');
      expect(user.preferences, {'lang': 'zh'});
    });

    test('toJson produces correct map', () {
      final user = AppUser(id: 2, username: 'alice', preferences: null);
      final json = user.toJson();
      expect(json['id'], 2);
      expect(json['username'], 'alice');
      expect(json['preferences'], null);
    });
  });

  group('CalendarEvent', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 10,
        'title': 'Meeting',
        'description': 'Team sync',
        'start_time': '2025-05-17T09:00:00',
        'end_time': '2025-05-17T10:00:00',
        'location': 'Room A',
        'category': 'meeting',
        'priority': 'high',
        'status': 'confirmed',
        'source': 'manual',
      };
      final event = CalendarEvent.fromJson(json);
      expect(event.id, 10);
      expect(event.title, 'Meeting');
      expect(event.description, 'Team sync');
      expect(event.startTime.year, 2025);
      expect(event.startTime.hour, 9);
      expect(event.endTime.hour, 10);
      expect(event.location, 'Room A');
      expect(event.category, 'meeting');
      expect(event.priority, 'high');
      expect(event.status, 'confirmed');
      expect(event.source, 'manual');
    });

    test('fromJson uses defaults for missing optional fields', () {
      final json = {
        'title': 'Quick event',
        'start_time': '2025-05-17T09:00:00',
        'end_time': '2025-05-17T09:30:00',
      };
      final event = CalendarEvent.fromJson(json);
      expect(event.id, null);
      expect(event.description, null);
      expect(event.category, 'other');
      expect(event.priority, 'medium');
      expect(event.status, 'confirmed');
      expect(event.source, 'manual');
    });

    test('toJson omits null optional fields', () {
      final event = CalendarEvent(
        title: 'Test',
        startTime: DateTime(2025, 5, 17, 9),
        endTime: DateTime(2025, 5, 17, 10),
      );
      final json = event.toJson();
      expect(json.containsKey('id'), false);
      expect(json.containsKey('description'), false);
      expect(json.containsKey('location'), false);
      expect(json['title'], 'Test');
    });

    test('copyWith creates modified copy', () {
      final event = CalendarEvent(
        id: 1,
        title: 'Original',
        startTime: DateTime(2025, 5, 17, 9),
        endTime: DateTime(2025, 5, 17, 10),
        status: 'tentative',
      );
      final copied = event.copyWith(title: 'Updated', status: 'confirmed');
      expect(copied.id, 1);
      expect(copied.title, 'Updated');
      expect(copied.status, 'confirmed');
      expect(copied.startTime, event.startTime);
    });
  });

  group('ChatMessage', () {
    test('isUser and isAssistant work correctly', () {
      final userMsg = ChatMessage(role: 'user', content: 'Hello');
      final aiMsg = ChatMessage(role: 'assistant', content: 'Hi there');
      expect(userMsg.isUser, true);
      expect(userMsg.isAssistant, false);
      expect(aiMsg.isUser, false);
      expect(aiMsg.isAssistant, true);
    });

    test('createdAt defaults to now', () {
      final before = DateTime.now();
      final msg = ChatMessage(role: 'user', content: 'test');
      final after = DateTime.now();
      expect(msg.createdAt.isAfter(before.subtract(const Duration(seconds: 1))), true);
      expect(msg.createdAt.isBefore(after.add(const Duration(seconds: 1))), true);
    });
  });

  group('Report', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 1,
        'report_type': 'weekly',
        'start_date': '2025-05-12',
        'end_date': '2025-05-18',
        'summary': 'Busy week',
        'statistics': {'meeting_hours': 5, 'task_count': 12},
        'created_at': '2025-05-18T23:00:00',
      };
      final report = Report.fromJson(json);
      expect(report.id, 1);
      expect(report.reportType, 'weekly');
      expect(report.startDate.year, 2025);
      expect(report.endDate.month, 5);
      expect(report.summary, 'Busy week');
      expect(report.statistics, {'meeting_hours': 5, 'task_count': 12});
    });

    test('fromJson handles null statistics', () {
      final json = {
        'id': 2,
        'report_type': 'monthly',
        'start_date': '2025-05-01',
        'end_date': '2025-05-31',
        'summary': 'Monthly report',
      };
      final report = Report.fromJson(json);
      expect(report.statistics, null);
    });
  });
}
