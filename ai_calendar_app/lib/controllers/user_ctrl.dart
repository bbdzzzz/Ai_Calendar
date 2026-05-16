import 'package:get/get.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/local_db.dart';
import '../services/ws_service.dart';

class UserController extends GetxController {
  final ApiService _api = Get.find<ApiService>();
  final WsService _ws = Get.find<WsService>();

  final _user = Rxn<AppUser>();
  final _isLoggedIn = false.obs;
  final _isLoading = false.obs;

  AppUser? get user => _user.value;
  bool get isLoggedIn => _isLoggedIn.value;
  bool get isLoading => _isLoading.value;

  @override
  void onInit() {
    super.onInit();
    _checkLogin();
  }

  void _checkLogin() {
    final token = LocalDb.getToken();
    final userId = LocalDb.getUserId();
    if (token != null && userId != null) {
      _isLoggedIn.value = true;
      _ws.connect(userId);
      _fetchMe();
    }
  }

  Future<void> _fetchMe() async {
    try {
      final data = await _api.getMe();
      _user.value = AppUser.fromJson(data);
    } catch (_) {
      _isLoggedIn.value = false;
      await LocalDb.clearToken();
    }
  }

  Future<bool> login(String username, String password) async {
    _isLoading.value = true;
    try {
      final data = await _api.login(username, password);
      final token = data['access_token'] as String?;
      final userId = data['user_id'] as int?;
      if (token != null && userId != null) {
        await LocalDb.setToken(token);
        await LocalDb.setUserId(userId);
        _isLoggedIn.value = true;
        _ws.connect(userId);
        await _fetchMe();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    } finally {
      _isLoading.value = false;
    }
  }

  Future<bool> register(String username, String password) async {
    _isLoading.value = true;
    try {
      final data = await _api.register(username, password);
      final token = data['access_token'] as String?;
      final userId = data['user_id'] as int?;
      if (token != null && userId != null) {
        await LocalDb.setToken(token);
        await LocalDb.setUserId(userId);
        _isLoggedIn.value = true;
        _ws.connect(userId);
        await _fetchMe();
        return true;
      }
      return false;
    } catch (_) {
      return false;
    } finally {
      _isLoading.value = false;
    }
  }

  Future<void> logout() async {
    _ws.disconnect();
    await LocalDb.clear();
    _user.value = null;
    _isLoggedIn.value = false;
    Get.offAllNamed('/login');
  }

  Future<void> updateServerUrl(String url) async {
    await LocalDb.setServerUrl(url);
    _api.updateBaseUrl('$url/api/v1');
  }
}
