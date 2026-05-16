import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/assistant_ctrl.dart';
import '../../models/conversation.dart';

class AssistantOverlay extends StatelessWidget {
  const AssistantOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    final ctrl = Get.find<AssistantController>();

    return Positioned(
      right: 16,
      bottom: 96,
      child: Obx(() {
        if (ctrl.state == AssistantState.idle) {
          return _buildFab(ctrl);
        }
        return const SizedBox.shrink();
      }),
    );
  }

  Widget _buildFab(AssistantController ctrl) {
    return FloatingActionButton(
      onPressed: () => _showPanel(),
      child: const Icon(Icons.mic),
    );
  }

  void _showPanel() {
    Get.dialog(
      const AssistantPanel(),
      barrierColor: Colors.black26,
      useSafeArea: false,
    );
  }
}

class AssistantPanel extends StatelessWidget {
  const AssistantPanel({super.key});

  @override
  Widget build(BuildContext context) {
    final ctrl = Get.find<AssistantController>();
    final theme = Theme.of(context);

    return Align(
      alignment: Alignment.bottomCenter,
      child: Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.15),
              blurRadius: 16,
            ),
          ],
        ),
        child: Column(
          children: [
            _buildHeader(ctrl, theme),
            Expanded(child: _buildMessages(ctrl, theme)),
            _buildPendingEvent(ctrl, theme),
            _buildInputArea(ctrl, theme),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(AssistantController ctrl, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: theme.colorScheme.outlineVariant),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.smart_toy, color: theme.colorScheme.primary),
          const SizedBox(width: 8),
          Text('AI 助手', style: theme.textTheme.titleMedium),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => Get.back(),
          ),
        ],
      ),
    );
  }

  Widget _buildMessages(AssistantController ctrl, ThemeData theme) {
    return Obx(
      () => ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: ctrl.messages.length + (ctrl.agentText.isNotEmpty ? 1 : 0),
        itemBuilder: (_, i) {
          if (i < ctrl.messages.length) {
            final msg = ctrl.messages[i];
            return _ChatBubble(message: msg, theme: theme);
          }
          return _ChatBubble(
            message: ChatMessage(role: 'assistant', content: ctrl.agentText),
            theme: theme,
            isStreaming: true,
          );
        },
      ),
    );
  }

  Widget _buildPendingEvent(AssistantController ctrl, ThemeData theme) {
    return Obx(() {
      final event = ctrl.pendingEvent;
      if (event == null) return const SizedBox.shrink();

      return Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: theme.colorScheme.primaryContainer,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(event['title'] ?? '', style: theme.textTheme.titleSmall),
            const SizedBox(height: 4),
            Text(
              '${event['start_time'] ?? ''} - ${event['end_time'] ?? ''}',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                FilledButton.tonal(
                  onPressed: () => ctrl.confirmEvent(false),
                  child: const Text('取消'),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: () => ctrl.confirmEvent(true),
                  child: const Text('确认'),
                ),
              ],
            ),
          ],
        ),
      );
    });
  }

  Widget _buildInputArea(AssistantController ctrl, ThemeData theme) {
    final textCtrl = TextEditingController();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(color: theme.colorScheme.outlineVariant),
        ),
      ),
      child: Obx(() {
        final state = ctrl.state;

        if (state == AssistantState.recording) {
          return Row(
            children: [
              const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  ctrl.asrPartial.isNotEmpty ? ctrl.asrPartial : '正在听...',
                  style: theme.textTheme.bodyMedium,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.stop_circle, size: 36, color: Colors.red),
                onPressed: () => ctrl.stopRecording(),
              ),
            ],
          );
        }

        if (state == AssistantState.processing) {
          return Row(
            children: [
              const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
              const SizedBox(width: 12),
              Expanded(child: Text('AI 正在思考...', style: theme.textTheme.bodyMedium)),
            ],
          );
        }

        if (state == AssistantState.speaking) {
          return Row(
            children: [
              const Icon(Icons.volume_up),
              const SizedBox(width: 12),
              Expanded(child: Text('正在播报...', style: theme.textTheme.bodyMedium)),
            ],
          );
        }

        return Row(
          children: [
            Expanded(
              child: TextField(
                controller: textCtrl,
                decoration: InputDecoration(
                  hintText: '输入消息...',
                  isDense: true,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
                onSubmitted: (v) {
                  if (v.trim().isNotEmpty) {
                    ctrl.sendText(v.trim());
                    textCtrl.clear();
                  }
                },
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.send),
              onPressed: () {
                final v = textCtrl.text.trim();
                if (v.isNotEmpty) {
                  ctrl.sendText(v);
                  textCtrl.clear();
                }
              },
            ),
            FloatingActionButton.small(
              onPressed: () => ctrl.startRecording(),
              child: const Icon(Icons.mic),
            ),
          ],
        );
      }),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final ThemeData theme;
  final bool isStreaming;

  const _ChatBubble({
    required this.message,
    required this.theme,
    this.isStreaming = false,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.7,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? theme.colorScheme.primary
              : theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(14),
            topRight: const Radius.circular(14),
            bottomLeft: Radius.circular(isUser ? 14 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 14),
          ),
        ),
        child: Text(
          message.content + (isStreaming ? '▌' : ''),
          style: TextStyle(
            color: isUser
                ? theme.colorScheme.onPrimary
                : theme.colorScheme.onSurface,
          ),
        ),
      ),
    );
  }
}
