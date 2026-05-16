import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:intl/intl.dart';
import '../../controllers/calendar_ctrl.dart';
import '../../models/event.dart';

class CalendarPage extends StatelessWidget {
  const CalendarPage({super.key});

  @override
  Widget build(BuildContext context) {
    final ctrl = Get.find<CalendarController>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('AI 语音日历'), centerTitle: true),
      body: Column(
        children: [
          _buildCalendar(ctrl, theme),
          const Divider(height: 1),
          Expanded(child: _buildEventList(ctrl, theme)),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Get.toNamed('/event/create');
          if (result == true) {
            ctrl.loadEvents();
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildCalendar(CalendarController ctrl, ThemeData theme) {
    return Obx(
      () => TableCalendar(
        firstDay: DateTime(2024, 1, 1),
        lastDay: DateTime(2027, 12, 31),
        focusedDay: ctrl.focusedDay,
        selectedDayPredicate: (day) => isSameDay(ctrl.selectedDay, day),
        onDaySelected: ctrl.selectDay,
        eventLoader: (day) {
          final key = DateTime(day.year, day.month, day.day);
          return ctrl.eventsMap[key] ?? [];
        },
        calendarStyle: CalendarStyle(
          selectedDecoration: BoxDecoration(
            color: theme.colorScheme.primary,
            shape: BoxShape.circle,
          ),
          todayDecoration: BoxDecoration(
            color: theme.colorScheme.primaryContainer,
            shape: BoxShape.circle,
          ),
          markerDecoration: BoxDecoration(
            color: theme.colorScheme.tertiary,
            shape: BoxShape.circle,
          ),
        ),
        headerStyle: const HeaderStyle(
          formatButtonVisible: false,
          titleCentered: true,
        ),
        calendarFormat: CalendarFormat.month,
      ),
    );
  }

  Widget _buildEventList(CalendarController ctrl, ThemeData theme) {
    return Obx(() {
      final events = ctrl.eventsForSelectedDay;
      if (events.isEmpty) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.event_available,
                size: 64,
                color: theme.colorScheme.outline,
              ),
              const SizedBox(height: 16),
              Text(
                '今天没有日程',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.outline,
                ),
              ),
            ],
          ),
        );
      }

      return ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        itemCount: events.length,
        itemBuilder: (_, i) => _EventCard(event: events[i], ctrl: ctrl),
      );
    });
  }
}

class _EventCard extends StatelessWidget {
  final CalendarEvent event;
  final CalendarController ctrl;

  const _EventCard({required this.event, required this.ctrl});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isTentative = event.status == 'tentative';
    final timeFmt = DateFormat('HH:mm');

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 4,
          height: 40,
          decoration: BoxDecoration(
            color: _categoryColor(event.category, theme),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        title: Text(
          event.title,
          style: TextStyle(
            decoration: isTentative ? TextDecoration.lineThrough : null,
          ),
        ),
        subtitle: Text(
          '${timeFmt.format(event.startTime)} - ${timeFmt.format(event.endTime)}'
          '${event.location != null ? ' · ${event.location}' : ''}',
        ),
        trailing: isTentative
            ? Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(
                      Icons.check_circle_outline,
                      color: Colors.green,
                    ),
                    onPressed: () => ctrl.confirmEvent(event.id!, true),
                  ),
                  IconButton(
                    icon: const Icon(Icons.cancel_outlined, color: Colors.red),
                    onPressed: () => ctrl.confirmEvent(event.id!, false),
                  ),
                ],
              )
            : null,
        onTap: () async {
          final result = await Get.toNamed('/event/detail', arguments: event);
          if (result == true) {
            ctrl.loadEvents();
          }
        },
        onLongPress: () => _confirmDelete(context),
      ),
    );
  }

  Color _categoryColor(String category, ThemeData theme) {
    switch (category) {
      case 'meeting':
        return Colors.blue;
      case 'work':
        return Colors.orange;
      case 'personal':
        return Colors.green;
      case 'health':
        return Colors.red;
      default:
        return theme.colorScheme.primary;
    }
  }

  void _confirmDelete(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('删除日程'),
        content: Text('确定删除「${event.title}」吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () {
              ctrl.deleteEvent(event.id!);
              Navigator.pop(context);
            },
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }
}
