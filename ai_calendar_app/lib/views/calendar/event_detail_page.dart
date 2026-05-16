import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../controllers/calendar_ctrl.dart';
import '../../models/event.dart';

class EventDetailPage extends StatefulWidget {
  const EventDetailPage({super.key});

  @override
  State<EventDetailPage> createState() => _EventDetailPageState();
}

class _EventDetailPageState extends State<EventDetailPage> {
  final _formKey = GlobalKey<FormState>();
  late final CalendarEvent _event;
  late final TextEditingController _titleCtrl;
  late final TextEditingController _descCtrl;
  late final TextEditingController _locationCtrl;
  late DateTime _startTime;
  late DateTime _endTime;
  late String _category;
  late String _priority;
  late String _status;
  bool _isEditing = false;
  bool _isLoading = false;

  static const _categoryOptions = {
    'meeting': '会议',
    'work': '工作',
    'personal': '个人',
    'health': '健康',
    'other': '其他',
  };

  static const _priorityOptions = {'high': '高', 'medium': '中', 'low': '低'};

  static const _statusOptions = {
    'confirmed': '已确认',
    'tentative': '待确认',
    'cancelled': '已取消',
  };

  @override
  void initState() {
    super.initState();
    _event = Get.arguments as CalendarEvent;
    _titleCtrl = TextEditingController(text: _event.title);
    _descCtrl = TextEditingController(text: _event.description ?? '');
    _locationCtrl = TextEditingController(text: _event.location ?? '');
    _startTime = _event.startTime;
    _endTime = _event.endTime;
    _category = _event.category;
    _priority = _event.priority;
    _status = _event.status;
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? '编辑日程' : '日程详情'),
        centerTitle: true,
        actions: [
          if (!_isEditing)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => setState(() => _isEditing = true),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildTitleField(theme),
            const SizedBox(height: 16),
            _buildTimeRange(theme),
            const SizedBox(height: 16),
            _buildLocationField(theme),
            const SizedBox(height: 16),
            _buildDescField(theme),
            const SizedBox(height: 16),
            _buildDropdowns(theme),
            const SizedBox(height: 24),
            if (_isEditing) _buildActions(theme),
          ],
        ),
      ),
    );
  }

  Widget _buildTitleField(ThemeData theme) {
    return TextFormField(
      controller: _titleCtrl,
      enabled: _isEditing,
      decoration: const InputDecoration(
        labelText: '标题',
        prefixIcon: Icon(Icons.title),
      ),
      validator: (v) => (v == null || v.trim().isEmpty) ? '请输入标题' : null,
    );
  }

  Widget _buildTimeRange(ThemeData theme) {
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
              onDateTap: _isEditing ? () => _pickDate(true) : null,
              onTimeTap: _isEditing ? () => _pickTime(true) : null,
            ),
            const Divider(),
            _buildTimeRow(
              icon: Icons.stop,
              label: '结束',
              dateTime: _endTime,
              dateFmt: dateFmt,
              timeFmt: timeFmt,
              onDateTap: _isEditing ? () => _pickDate(false) : null,
              onTimeTap: _isEditing ? () => _pickTime(false) : null,
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
    VoidCallback? onDateTap,
    VoidCallback? onTimeTap,
  }) {
    return Row(
      children: [
        Icon(icon, size: 18),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
        const Spacer(),
        _tappableChip(dateFmt.format(dateTime), onDateTap),
        const SizedBox(width: 8),
        _tappableChip(timeFmt.format(dateTime), onTimeTap),
      ],
    );
  }

  Widget _tappableChip(String text, VoidCallback? onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: onTap != null
              ? Theme.of(context).colorScheme.surfaceContainerHighest
              : null,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(text),
      ),
    );
  }

  Widget _buildLocationField(ThemeData theme) {
    return TextFormField(
      controller: _locationCtrl,
      enabled: _isEditing,
      decoration: const InputDecoration(
        labelText: '地点',
        prefixIcon: Icon(Icons.location_on_outlined),
      ),
    );
  }

  Widget _buildDescField(ThemeData theme) {
    return TextFormField(
      controller: _descCtrl,
      enabled: _isEditing,
      decoration: const InputDecoration(
        labelText: '描述',
        prefixIcon: Icon(Icons.notes),
      ),
      maxLines: 3,
    );
  }

  Widget _buildDropdowns(ThemeData theme) {
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
            const SizedBox(height: 12),
            _buildDropdown(
              '状态',
              _status,
              _statusOptions,
              (v) => setState(() => _status = v!),
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
          onChanged: _isEditing ? onChanged : null,
        ),
      ],
    );
  }

  Widget _buildActions(ThemeData theme) {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton(
            onPressed: () => setState(() => _isEditing = false),
            child: const Text('取消'),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: FilledButton(
            onPressed: _isLoading ? null : _save,
            child: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('保存'),
          ),
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
      await ctrl.updateEvent(_event.id!, {
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
        'status': _status,
      });
      Get.back(result: true);
      Get.snackbar('成功', '日程已更新', snackPosition: SnackPosition.BOTTOM);
    } catch (_) {
      Get.snackbar('错误', '保存失败', snackPosition: SnackPosition.BOTTOM);
    }
    setState(() => _isLoading = false);
  }
}
