import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../models/report.dart';

class ReportDetailPage extends StatelessWidget {
  const ReportDetailPage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final Report report = Get.arguments as Report;
    final dateFmt = DateFormat('yyyy-MM-dd');

    return Scaffold(
      appBar: AppBar(title: const Text('周报详情'), centerTitle: true),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildDateRange(report, theme, dateFmt),
          const SizedBox(height: 16),
          _buildSummary(report, theme),
          if (report.statistics != null) ...[
            const SizedBox(height: 16),
            _buildStatistics(report, theme),
          ],
          const SizedBox(height: 16),
          _buildMeta(report, theme, dateFmt),
        ],
      ),
    );
  }

  Widget _buildDateRange(Report report, ThemeData theme, DateFormat dateFmt) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.date_range, color: theme.colorScheme.primary),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '统计周期',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${dateFmt.format(report.startDate)} ~ ${dateFmt.format(report.endDate)}',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                report.reportType == 'weekly' ? '周报' : '月报',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummary(Report report, ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.summarize,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  '摘要',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              report.summary.isNotEmpty ? report.summary : '暂无摘要内容',
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatistics(Report report, ThemeData theme) {
    final stats = report.statistics!;
    final entries = stats.entries.toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.bar_chart,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  '统计数据',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...entries.map((e) => _buildStatRow(e.key, e.value, theme)),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, dynamic value, ThemeData theme) {
    String displayValue;
    if (value is Map) {
      displayValue = value.entries
          .map((e) => '${e.key}: ${e.value}')
          .join(', ');
    } else if (value is List) {
      displayValue = value.join(', ');
    } else {
      displayValue = value.toString();
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(displayValue, style: theme.textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }

  Widget _buildMeta(Report report, ThemeData theme, DateFormat dateFmt) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.access_time, color: theme.colorScheme.outline, size: 16),
            const SizedBox(width: 8),
            Text(
              '生成于 ${dateFmt.format(report.createdAt)}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.outline,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
