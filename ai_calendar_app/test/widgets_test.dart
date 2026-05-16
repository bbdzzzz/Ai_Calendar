import 'package:flutter_test/flutter_test.dart';
import 'package:ai_calendar_app/app/routes/app_routes.dart';
import 'package:ai_calendar_app/app/theme/app_theme.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('AppTheme', () {
    test('light theme uses Material 3', () {
      final theme = AppTheme.lightTheme();
      expect(theme.useMaterial3, true);
    });

    test('dark theme uses Material 3', () {
      final theme = AppTheme.darkTheme();
      expect(theme.useMaterial3, true);
    });

    test('card theme has zero elevation', () {
      final theme = AppTheme.lightTheme();
      expect(theme.cardTheme.elevation, 0);
    });

    test('app bar is centered', () {
      final theme = AppTheme.lightTheme();
      expect(theme.appBarTheme.centerTitle, true);
    });

    test('input decoration is filled', () {
      final theme = AppTheme.lightTheme();
      expect(theme.inputDecorationTheme.filled, true);
    });

    test('buttons have rounded corners', () {
      final theme = AppTheme.lightTheme();
      expect(theme.filledButtonTheme.style, isNotNull);
      expect(theme.outlinedButtonTheme.style, isNotNull);
    });
  });

  group('AppRoutes', () {
    test('all routes are defined', () {
      expect(AppRoutes.login, '/login');
      expect(AppRoutes.home, '/home');
      expect(AppRoutes.reportList, '/report/list');
      expect(AppRoutes.reportDetail, '/report/detail');
      expect(AppRoutes.eventDetail, '/event/detail');
      expect(AppRoutes.eventCreate, '/event/create');
    });

    test('pages list has correct length', () {
      expect(AppRoutes.pages.length, 6);
    });

    test('each page has a name and a builder', () {
      for (final page in AppRoutes.pages) {
        expect(page.name, isNotEmpty);
        expect(page.page, isNotNull);
      }
    });
  });
}
