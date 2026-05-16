import 'package:get/get.dart';
import '../../views/auth/login_page.dart';
import '../../views/home_page.dart';
import '../../views/report/report_list_page.dart';
import '../../views/report/report_detail_page.dart';
import '../../views/calendar/event_detail_page.dart';
import '../../views/calendar/event_create_page.dart';

class AppRoutes {
  static const login = '/login';
  static const home = '/home';
  static const reportList = '/report/list';
  static const reportDetail = '/report/detail';
  static const eventDetail = '/event/detail';
  static const eventCreate = '/event/create';

  static final pages = [
    GetPage(name: login, page: () => LoginPage()),
    GetPage(name: home, page: () => HomePage()),
    GetPage(name: reportList, page: () => const ReportListPage()),
    GetPage(name: reportDetail, page: () => const ReportDetailPage()),
    GetPage(name: eventDetail, page: () => const EventDetailPage()),
    GetPage(name: eventCreate, page: () => const EventCreatePage()),
  ];
}
