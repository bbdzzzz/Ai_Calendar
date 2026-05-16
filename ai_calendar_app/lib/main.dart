import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'app/routes/app_routes.dart';
import 'app/theme/app_theme.dart';
import 'controllers/user_ctrl.dart';
import 'controllers/calendar_ctrl.dart';
import 'controllers/assistant_ctrl.dart';
import 'controllers/report_ctrl.dart';
import 'services/api_service.dart';
import 'services/ws_service.dart';
import 'services/audio_recorder.dart';
import 'services/audio_player.dart';
import 'services/local_db.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await LocalDb.init();

  await _initServices();

  final userCtrl = Get.find<UserController>();
  final initialRoute = userCtrl.isLoggedIn ? AppRoutes.home : AppRoutes.login;

  runApp(MyApp(initialRoute: initialRoute));
}

Future<void> _initServices() async {
  await Get.putAsync<ApiService>(() => ApiService().init());
  Get.put<WsService>(WsService());
  Get.put<AudioRecorderService>(AudioRecorderService());
  Get.put<AudioPlayerService>(AudioPlayerService());
  Get.put<UserController>(UserController());
  Get.put<CalendarController>(CalendarController());
  Get.put<AssistantController>(AssistantController());
  Get.put<ReportController>(ReportController());
}

class MyApp extends StatelessWidget {
  final String initialRoute;

  const MyApp({super.key, required this.initialRoute});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      builder: (_, _) => GetMaterialApp(
        title: 'AI 语音日历',
        theme: AppTheme.lightTheme(),
        darkTheme: AppTheme.darkTheme(),
        initialRoute: initialRoute,
        getPages: AppRoutes.pages,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
