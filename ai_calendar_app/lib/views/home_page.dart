import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'calendar/calendar_page.dart';
import 'report/report_list_page.dart';
import 'assistant/assistant_overlay.dart';
import 'profile/profile_page.dart';

class HomePage extends StatelessWidget {
  HomePage({super.key});

  final _currentIndex = 0.obs;

  final _pages = const [
    CalendarPage(),
    ReportListPage(),
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Obx(() => IndexedStack(index: _currentIndex.value, children: _pages)),
          const AssistantOverlay(),
        ],
      ),
      bottomNavigationBar: Obx(() => NavigationBar(
            selectedIndex: _currentIndex.value,
            onDestinationSelected: (i) => _currentIndex.value = i,
            destinations: const [
              NavigationDestination(icon: Icon(Icons.calendar_month), label: '日历'),
              NavigationDestination(icon: Icon(Icons.assessment), label: '周报'),
              NavigationDestination(icon: Icon(Icons.person), label: '我的'),
            ],
          )),
    );
  }
}
