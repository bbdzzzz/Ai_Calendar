import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/user_ctrl.dart';
import '../../services/local_db.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final userCtrl = Get.find<UserController>();
    final theme = Theme.of(context);
    final serverCtrl = TextEditingController(text: LocalDb.getServerUrl());

    return Scaffold(
      appBar: AppBar(title: const Text('我的'), centerTitle: true),
      body: ListView(
        children: [
          const SizedBox(height: 24),
          CircleAvatar(
            radius: 48,
            backgroundColor: theme.colorScheme.primaryContainer,
            child: Icon(Icons.person, size: 48, color: theme.colorScheme.onPrimaryContainer),
          ),
          const SizedBox(height: 16),
          Obx(() => Text(
                userCtrl.user?.username ?? '用户',
                textAlign: TextAlign.center,
                style: theme.textTheme.titleLarge,
              )),
          const SizedBox(height: 32),
          _buildSection(theme, '服务器设置', [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: TextField(
                controller: serverCtrl,
                decoration: const InputDecoration(
                  labelText: '服务器地址',
                  hintText: 'http://192.168.1.100:8000',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (v) => userCtrl.updateServerUrl(v.trim()),
              ),
            ),
          ]),
          const SizedBox(height: 16),
          _buildSection(theme, '关于', [
            ListTile(leading: const Icon(Icons.info_outline), title: Text('版本 1.0.0')),
            ListTile(leading: const Icon(Icons.description_outlined), title: Text('开发文档')),
          ]),
          const SizedBox(height: 32),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: FilledButton.tonal(
              onPressed: () => _confirmLogout(context, userCtrl),
              style: FilledButton.styleFrom(backgroundColor: Colors.red.shade50, foregroundColor: Colors.red),
              child: const Text('退出登录'),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildSection(ThemeData theme, String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Text(title, style: theme.textTheme.titleSmall?.copyWith(color: theme.colorScheme.primary)),
        ),
        ...children,
      ],
    );
  }

  void _confirmLogout(BuildContext context, UserController userCtrl) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('退出登录'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('取消')),
          FilledButton(onPressed: () => userCtrl.logout(), child: const Text('确定')),
        ],
      ),
    );
  }
}
