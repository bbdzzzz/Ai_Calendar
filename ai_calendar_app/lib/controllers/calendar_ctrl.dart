import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../models/event.dart';
import '../services/api_service.dart';
import '../services/ws_service.dart';

class CalendarController extends GetxController {
  final ApiService _api = Get.find<ApiService>();

  final _events = <CalendarEvent>[].obs;
  final _selectedDay = DateTime.now().obs;
  final _focusedDay = DateTime.now().obs;
  final _isLoading = false.obs;

  List<CalendarEvent> get events => _events;
  DateTime get selectedDay => _selectedDay.value;
  DateTime get focusedDay => _focusedDay.value;
  bool get isLoading => _isLoading.value;

  List<CalendarEvent> get eventsForSelectedDay => _events
      .where(
        (e) =>
            e.startTime.year == _selectedDay.value.year &&
            e.startTime.month == _selectedDay.value.month &&
            e.startTime.day == _selectedDay.value.day,
      )
      .toList();

  Map<DateTime, List<CalendarEvent>> get eventsMap {
    final map = <DateTime, List<CalendarEvent>>{};
    for (final e in _events) {
      final key = DateTime(
        e.startTime.year,
        e.startTime.month,
        e.startTime.day,
      );
      map.putIfAbsent(key, () => []).add(e);
    }
    return map;
  }

  @override
  void onInit() {
    super.onInit();
    loadEvents();

    final ws = Get.find<WsService>();
    ws.addMessageHandler((type, payload) {
      if (type == 'event_upsert') {
        handleEventUpsert(payload);
      }
    });
  }

  Future<void> loadEvents() async {
    _isLoading.value = true;
    try {
      final now = DateTime.now();
      final start = DateTime(now.year, now.month - 1, 1);
      final end = DateTime(now.year, now.month + 2, 0);
      final data = await _api.getEvents(startDate: start, endDate: end);
      _events.value = data
          .map((e) => CalendarEvent.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      Get.snackbar('错误', '加载日程失败', snackPosition: SnackPosition.BOTTOM);
    }
    _isLoading.value = false;
  }

  void selectDay(DateTime day, DateTime focused) {
    _selectedDay.value = day;
    _focusedDay.value = focused;
  }

  void handleEventUpsert(Map<String, dynamic> payload) {
    final event = CalendarEvent.fromJson(payload);
    final idx = _events.indexWhere((e) => e.id == event.id);
    if (idx >= 0) {
      _events[idx] = event;
    } else {
      _events.add(event);
    }
  }

  Future<void> confirmEvent(int eventId, bool confirmed) async {
    final ws = Get.find<WsService>();
    ws.sendEventConfirm(eventId.toString(), confirmed);
    if (!confirmed) {
      _events.removeWhere((e) => e.id == eventId);
    } else {
      final idx = _events.indexWhere((e) => e.id == eventId);
      if (idx >= 0) {
        _events[idx] = _events[idx].copyWith(status: 'confirmed');
      }
    }
  }

  Future<void> deleteEvent(int id) async {
    try {
      await _api.deleteEvent(id);
      _events.removeWhere((e) => e.id == id);
    } catch (_) {
      Get.snackbar('错误', '删除失败', snackPosition: SnackPosition.BOTTOM);
    }
  }

  Future<void> updateEvent(int id, Map<String, dynamic> data) async {
    try {
      final res = await _api.updateEvent(id, data);
      final updated = CalendarEvent.fromJson(res);
      final idx = _events.indexWhere((e) => e.id == id);
      if (idx >= 0) {
        _events[idx] = updated;
      }
    } catch (_) {
      Get.snackbar('错误', '更新日程失败', snackPosition: SnackPosition.BOTTOM);
      rethrow;
    }
  }

  Future<void> createEvent(Map<String, dynamic> data) async {
    try {
      final res = await _api.createEvent(data);
      final event = CalendarEvent.fromJson(res);
      _events.add(event);
    } catch (_) {
      Get.snackbar('错误', '创建日程失败', snackPosition: SnackPosition.BOTTOM);
      rethrow;
    }
  }

  String formatEventTime(CalendarEvent e) {
    final fmt = DateFormat('HH:mm');
    return '${fmt.format(e.startTime)} - ${fmt.format(e.endTime)}';
  }
}
