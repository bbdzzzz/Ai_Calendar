import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../controllers/report_ctrl.dart';
import '../../models/report.dart';

class ReportListPage extends StatelessWidget {
  const ReportListPage({super.key});

  @override
  Widget build(BuildContext context) {
    final ctrl = Get.find<ReportController>();
    final theme = Theme.of(context);
    final dateFmt = DateFormat('yyyy-MM-dd');

    return Scaffold(
      appBar: AppBar(title: const Text('周报'), centerTitle: true),
      body: Column(
        children: [
          _buildTypeSelector(ctrl, theme),
          const Divider(height: 1),
          Expanded(child: _buildList(ctrl, theme, dateFmt)),
        ],
      ),
    );
  }

  Widget _buildTypeSelector(ReportController ctrl, ThemeData theme) {
    return Obx(() => Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'weekly', label: Text('周报')),
              ButtonSegment(value: 'monthly', label: Text('月报')),
            ],
            selected: {ctrl.selectedType},
            onSelectionChanged: (s) => ctrl.setType(s.first),
          ),
        ));
  }

  Widget _buildList(ReportController ctrl, ThemeData theme, DateFormat dateFmt) {
    return Obx(() {
      if (ctrl.isLoading) {
        return const Center(child: CircularProgressIndicator());
      }

      final reports = ctrl.reports;
      if (reports.isEmpty) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.assessment_outlined, size: 64, color: theme.colorScheme.outline),
              const SizedBox(height: 16),
              Text('暂无周报', style: theme.textTheme.bodyLarge?.copyWith(color: theme.colorScheme.outline)),
            ],
          ),
        );
      }

      return RefreshIndicator(
        onRefresh: ctrl.loadReports,
        child: ListView.builder(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          itemCount: reports.length,
          itemBuilder: (_, i) => _ReportCard(report: reports[i], dateFmt: dateFmt),
        ),
      );
    });
  }
}

class _ReportCard extends StatelessWidget {
  final Report report;
  final DateFormat dateFmt;

  const _ReportCard({required this.report, required this.dateFmt});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 4,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        title: Text(
          '${dateFmt.format(report.startDate)} ~ ${dateFmt.format(report.endDate)}',
          style: theme.textTheme.titleSmall,
        ),
        subtitle: Text(
          report.summary.isNotEmpty ? report.summary : '暂无摘要',
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => Get.toNamed('/report/detail', arguments: report),
      ),
    );
  }
}
