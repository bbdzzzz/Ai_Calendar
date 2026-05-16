import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../controllers/calendar_ctrl.dart';

class EventCreatePage extends StatefulWidget {
  const EventCreatePage({super.key});

  @override
  State<EventCreatePage> createState() => _EventCreatePageState();
}

class _EventCreatePageState extends State<EventCreatePage> {
  final _formKey = GlobalKey<FormState>();
  final _titleCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _locationCtrl = TextEditingController();

  DateTime _startTime = DateTime.now().add(const Duration(hours: 1));
  DateTime _endTime = DateTime.now().add(const Duration(hours: 2));
  String _category = 'other';
  String _priority = 'medium';

  bool _isLoading = false;

  static const _categoryOptions = {
    'meeting': '会议',
    'work': '工作',
    'personal': '个人',
    'health': '健康',
    'other': '其他',
  };

  static const _priorityOptions = {'high': '高', 'medium': '中', 'low': '低'};

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('新建日程'),
        centerTitle: true,
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _save,
            child: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('保存'),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _titleCtrl,
              decoration: const InputDecoration(
                labelText: '标题',
                prefixIcon: Icon(Icons.title),
              ),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? '请输入标题' : null,
            ),
            const SizedBox(height: 16),
            _buildTimeRange(),
            const SizedBox(height: 16),
            TextFormField(
              controller: _locationCtrl,
              decoration: const InputDecoration(
                labelText: '地点',
                prefixIcon: Icon(Icons.location_on_outlined),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descCtrl,
              decoration: const InputDecoration(
                labelText: '描述',
                prefixIcon: Icon(Icons.notes),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            _buildDropdowns(),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeRange() {
    final dateFmt = DateFormat('yyyy-MM-dd');
    final timeFmt = DateFormat('HH:mm');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            _buildTimeRow(
              icon: Icons.play_arrow,
              label: '开始',
              dateTime: _startTime,
              dateFmt: dateFmt,
              timeFmt: timeFmt,
              isStart: true,
            ),
            const Divider(),
            _buildTimeRow(
              icon: Icons.stop,
              label: '结束',
              dateTime: _endTime,
              dateFmt: dateFmt,
              timeFmt: timeFmt,
              isStart: false,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeRow({
    required IconData icon,
    required String label,
    required DateTime dateTime,
    required DateFormat dateFmt,
    required DateFormat timeFmt,
    required bool isStart,
  }) {
    return Row(
      children: [
        Icon(icon, size: 18),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
        const Spacer(),
        _tappableChip(dateFmt.format(dateTime), () => _pickDate(isStart)),
        const SizedBox(width: 8),
        _tappableChip(timeFmt.format(dateTime), () => _pickTime(isStart)),
      ],
    );
  }

  Widget _tappableChip(String text, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(text),
      ),
    );
  }

  Widget _buildDropdowns() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            _buildDropdown(
              '分类',
              _category,
              _categoryOptions,
              (v) => setState(() => _category = v!),
            ),
            const SizedBox(height: 12),
            _buildDropdown(
              '优先级',
              _priority,
              _priorityOptions,
              (v) => setState(() => _priority = v!),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDropdown(
    String label,
    String value,
    Map<String, String> options,
    ValueChanged<String?> onChanged,
  ) {
    return Row(
      children: [
        SizedBox(width: 80, child: Text(label)),
        const Spacer(),
        DropdownButton<String>(
          value: value,
          underline: const SizedBox.shrink(),
          items: options.entries
              .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value)))
              .toList(),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Future<void> _pickDate(bool isStart) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: isStart ? _startTime : _endTime,
      firstDate: DateTime(2024),
      lastDate: DateTime(2030),
    );
    if (picked != null) {
      setState(() {
        if (isStart) {
          _startTime = DateTime(
            picked.year,
            picked.month,
            picked.day,
            _startTime.hour,
            _startTime.minute,
          );
        } else {
          _endTime = DateTime(
            picked.year,
            picked.month,
            picked.day,
            _endTime.hour,
            _endTime.minute,
          );
        }
      });
    }
  }

  Future<void> _pickTime(bool isStart) async {
    final picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(isStart ? _startTime : _endTime),
    );
    if (picked != null) {
      setState(() {
        if (isStart) {
          _startTime = DateTime(
            _startTime.year,
            _startTime.month,
            _startTime.day,
            picked.hour,
            picked.minute,
          );
        } else {
          _endTime = DateTime(
            _endTime.year,
            _endTime.month,
            _endTime.day,
            picked.hour,
            picked.minute,
          );
        }
      });
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    if (_startTime.isAfter(_endTime) || _startTime == _endTime) {
      Get.snackbar('错误', '结束时间必须晚于开始时间', snackPosition: SnackPosition.BOTTOM);
      return;
    }

    setState(() => _isLoading = true);
    try {
      final ctrl = Get.find<CalendarController>();
      await ctrl.createEvent({
        'title': _titleCtrl.text.trim(),
        'description': _descCtrl.text.trim().isEmpty
            ? null
            : _descCtrl.text.trim(),
        'start_time': _startTime.toIso8601String(),
        'end_time': _endTime.toIso8601String(),
        'location': _locationCtrl.text.trim().isEmpty
            ? null
            : _locationCtrl.text.trim(),
        'category': _category,
        'priority': _priority,
        'status': 'confirmed',
        'source': 'manual',
      });
      Get.back(result: true);
      Get.snackbar('成功', '日程已创建', snackPosition: SnackPosition.BOTTOM);
    } catch (_) {
      Get.snackbar('错误', '创建失败', snackPosition: SnackPosition.BOTTOM);
    }
    setState(() => _isLoading = false);
  }
}
