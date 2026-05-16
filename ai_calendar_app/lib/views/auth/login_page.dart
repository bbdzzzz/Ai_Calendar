import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/user_ctrl.dart';

class LoginPage extends StatelessWidget {
  LoginPage({super.key});

  final _usernameCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  final _isRegister = false.obs;

  @override
  Widget build(BuildContext context) {
    final userCtrl = Get.find<UserController>();

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.calendar_month, size: 80, color: Theme.of(context).colorScheme.primary),
                  const SizedBox(height: 16),
                  Text('AI 语音日历', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 48),
                  TextFormField(
                    controller: _usernameCtrl,
                    decoration: const InputDecoration(labelText: '用户名', prefixIcon: Icon(Icons.person_outline)),
                    validator: (v) => (v == null || v.trim().isEmpty) ? '请输入用户名' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _passwordCtrl,
                    decoration: const InputDecoration(labelText: '密码', prefixIcon: Icon(Icons.lock_outline)),
                    obscureText: true,
                    validator: (v) => (v == null || v.length < 4) ? '密码至少4位' : null,
                  ),
                  const SizedBox(height: 32),
                  Obx(() => SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: FilledButton(
                          onPressed: userCtrl.isLoading ? null : _submit,
                          child: userCtrl.isLoading
                              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                              : Text(_isRegister.value ? '注册' : '登录'),
                        ),
                      )),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () => _isRegister.value = !_isRegister.value,
                    child: Text(_isRegister.value ? '已有账号？去登录' : '没有账号？去注册'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final userCtrl = Get.find<UserController>();
    final ok = _isRegister.value
        ? await userCtrl.register(_usernameCtrl.text.trim(), _passwordCtrl.text)
        : await userCtrl.login(_usernameCtrl.text.trim(), _passwordCtrl.text);
    if (ok) {
      Get.offAllNamed('/home');
    } else {
      Get.snackbar('错误', _isRegister.value ? '注册失败，用户名可能已存在' : '登录失败，请检查用户名和密码',
          snackPosition: SnackPosition.BOTTOM);
    }
  }
}
