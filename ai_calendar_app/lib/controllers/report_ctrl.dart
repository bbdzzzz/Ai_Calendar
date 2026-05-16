import 'package:get/get.dart';
import '../models/report.dart';
import '../services/api_service.dart';

class ReportController extends GetxController {
  final ApiService _api = Get.find<ApiService>();

  final _reports = <Report>[].obs;
  final _isLoading = false.obs;
  final _selectedType = 'weekly'.obs;

  List<Report> get reports => _reports;
  bool get isLoading => _isLoading.value;
  String get selectedType => _selectedType.value;

  @override
  void onInit() {
    super.onInit();
    loadReports();
  }

  Future<void> loadReports() async {
    _isLoading.value = true;
    try {
      final data = await _api.getReports(reportType: _selectedType.value);
      _reports.value = data
          .map((e) => Report.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      Get.snackbar('错误', '加载周报失败', snackPosition: SnackPosition.BOTTOM);
    }
    _isLoading.value = false;
  }

  void setType(String type) {
    _selectedType.value = type;
    loadReports();
  }

  Future<Report?> getReportDetail(int id) async {
    try {
      final data = await _api.getReport(id);
      return Report.fromJson(data);
    } catch (_) {
      Get.snackbar('错误', '加载周报详情失败', snackPosition: SnackPosition.BOTTOM);
      return null;
    }
  }
}
