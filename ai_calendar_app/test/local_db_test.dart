import 'package:flutter_test/flutter_test.dart';
import 'package:ai_calendar_app/services/local_db.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('LocalDb', () {
    setUp(() async {
      await LocalDb.initForTest();
    });

    tearDown(() async {
      await LocalDb.clear();
    });

    test('token operations', () async {
      expect(LocalDb.getToken(), null);

      await LocalDb.setToken('test-jwt-token');
      expect(LocalDb.getToken(), 'test-jwt-token');

      await LocalDb.clearToken();
      expect(LocalDb.getToken(), null);
    });

    test('userId operations', () async {
      expect(LocalDb.getUserId(), null);

      await LocalDb.setUserId(42);
      expect(LocalDb.getUserId(), 42);
    });

    test('serverUrl defaults correctly', () async {
      final url = LocalDb.getServerUrl();
      expect(url, 'http://10.0.2.2:8000');

      await LocalDb.setServerUrl('http://192.168.1.100:8000');
      expect(LocalDb.getServerUrl(), 'http://192.168.1.100:8000');
    });

    test('clear removes all data', () async {
      await LocalDb.setToken('token');
      await LocalDb.setUserId(1);
      await LocalDb.clear();

      expect(LocalDb.getToken(), null);
      expect(LocalDb.getUserId(), null);
    });
  });
}
