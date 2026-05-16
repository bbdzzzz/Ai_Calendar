import 'package:hive/hive.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class LocalDb {
  static const _tokenKey = 'auth_token';
  static const _userIdKey = 'user_id';
  static const _serverUrlKey = 'server_url';
  static Box? _box;

  static Future<void> init() async {
    if (_box != null && _box!.isOpen) return;
    final dir = await getApplicationDocumentsDirectory();
    Hive.init(dir.path);
    _box = await Hive.openBox('ai_calendar');
  }

  static Future<void> initForTest() async {
    if (_box != null && _box!.isOpen) return;
    final dir = Directory.systemTemp.createTempSync('hive_test_');
    Hive.init(dir.path);
    _box = await Hive.openBox('ai_calendar_test');
  }

  static Box get _b => _box!;

  static String? getToken() => _b.get(_tokenKey);
  static Future<void> setToken(String token) => _b.put(_tokenKey, token);
  static Future<void> clearToken() => _b.delete(_tokenKey);

  static int? getUserId() => _b.get(_userIdKey);
  static Future<void> setUserId(int id) => _b.put(_userIdKey, id);

  static String getServerUrl() =>
      _b.get(_serverUrlKey, defaultValue: 'http://10.0.2.2:8000') as String;
  static Future<void> setServerUrl(String url) => _b.put(_serverUrlKey, url);

  static Future<void> clear() => _b.clear();
}
