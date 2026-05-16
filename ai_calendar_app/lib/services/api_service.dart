import 'package:dio/dio.dart';
import 'package:get/get.dart' hide Response;
import 'local_db.dart';

class ApiService extends GetxService {
  late final Dio _dio;

  Future<ApiService> init() async {
    _dio = Dio(
      BaseOptions(
        baseUrl: 'http://10.0.2.2:8000/api/v1',
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 30),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = LocalDb.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (e, handler) {
          if (e.response?.statusCode == 401) {
            LocalDb.clearToken();
            Get.offAllNamed('/login');
          } else if (e.type == DioExceptionType.connectionError ||
              e.type == DioExceptionType.connectionTimeout) {
            Get.snackbar(
              '网络错误',
              '无法连接服务器，请检查网络设置',
              snackPosition: SnackPosition.BOTTOM,
            );
          }
          handler.next(e);
        },
      ),
    );

    return this;
  }

  void updateBaseUrl(String url) {
    _dio.options.baseUrl = url;
  }

  Future<Map<String, dynamic>> register(
    String username,
    String password,
  ) async {
    final res = await _dio.post(
      '/auth/register',
      data: {'username': username, 'password': password},
    );
    return res.data;
  }

  Future<Map<String, dynamic>> login(String username, String password) async {
    final res = await _dio.post(
      '/auth/login',
      data: {'username': username, 'password': password},
    );
    return res.data;
  }

  Future<Map<String, dynamic>> getMe() async {
    final res = await _dio.get('/auth/me');
    return res.data;
  }

  Future<List<dynamic>> getEvents({
    DateTime? startDate,
    DateTime? endDate,
    String? category,
    String? status,
  }) async {
    final params = <String, dynamic>{};
    if (startDate != null) params['start_date'] = startDate.toIso8601String();
    if (endDate != null) params['end_date'] = endDate.toIso8601String();
    if (category != null) params['category'] = category;
    if (status != null) params['status'] = status;
    final res = await _dio.get('/events', queryParameters: params);
    return res.data;
  }

  Future<Map<String, dynamic>> createEvent(Map<String, dynamic> data) async {
    final res = await _dio.post('/events', data: data);
    return res.data;
  }

  Future<Map<String, dynamic>> updateEvent(
    int id,
    Map<String, dynamic> data,
  ) async {
    final res = await _dio.put('/events/$id', data: data);
    return res.data;
  }

  Future<void> deleteEvent(int id) async {
    await _dio.delete('/events/$id');
  }

  Future<List<dynamic>> getReports({String? reportType}) async {
    final params = <String, dynamic>{};
    if (reportType != null) params['report_type'] = reportType;
    final res = await _dio.get('/reports', queryParameters: params);
    return res.data;
  }

  Future<Map<String, dynamic>> getReport(int id) async {
    final res = await _dio.get('/reports/$id');
    return res.data;
  }
}
