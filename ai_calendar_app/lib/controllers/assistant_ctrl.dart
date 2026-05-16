import 'dart:typed_data';

import 'package:get/get.dart';
import '../models/conversation.dart';
import '../services/ws_service.dart';
import '../services/audio_recorder.dart';
import '../services/audio_player.dart';
import '../services/local_db.dart';
import '../controllers/calendar_ctrl.dart';

enum AssistantState { idle, recording, processing, speaking }

class AssistantController extends GetxController {
  final WsService _ws = Get.find<WsService>();
  final AudioRecorderService _recorder = Get.find<AudioRecorderService>();
  final AudioPlayerService _player = Get.find<AudioPlayerService>();

  final _state = AssistantState.idle.obs;
  final _messages = <ChatMessage>[].obs;
  final _asrPartial = ''.obs;
  final _agentText = ''.obs;
  final _pendingEvent = Rxn<Map<String, dynamic>>();

  AssistantState get state => _state.value;
  List<ChatMessage> get messages => _messages;
  String get asrPartial => _asrPartial.value;
  String get agentText => _agentText.value;
  Map<String, dynamic>? get pendingEvent => _pendingEvent.value;
  bool get isRecording => _state.value == AssistantState.recording;

  @override
  void onInit() {
    super.onInit();
    _ws.addMessageHandler(_handleMessage);
    _ws.addBinaryHandler(_handleBinary);
  }

  void _handleMessage(String type, Map<String, dynamic> payload) {
    switch (type) {
      case 'asr_partial':
        _asrPartial.value = payload['text'] ?? '';
        break;
      case 'asr_final':
        _asrPartial.value = '';
        final text = payload['text'] ?? '';
        if (text.isNotEmpty) {
          _messages.add(ChatMessage(role: 'user', content: text));
          _state.value = AssistantState.processing;
        }
        break;
      case 'agent_text_delta':
        final delta = payload['delta'] ?? '';
        _agentText.value += delta;
        break;
      case 'agent_audio_done':
        if (_agentText.value.isNotEmpty) {
          _messages.add(
            ChatMessage(role: 'assistant', content: _agentText.value),
          );
          _agentText.value = '';
        }
        _player.play();
        _state.value = AssistantState.speaking;
        Future.delayed(const Duration(seconds: 3), () {
          if (_state.value == AssistantState.speaking) {
            _state.value = AssistantState.idle;
          }
        });
        break;
      case 'event_upsert':
        _pendingEvent.value = payload;
        final calCtrl = Get.find<CalendarController>();
        calCtrl.handleEventUpsert(payload);
        break;
    }
  }

  void _handleBinary(Uint8List data) {
    _player.feed(data);
  }

  Future<void> startRecording() async {
    final userId = LocalDb.getUserId();
    if (userId == null) return;

    if (!_ws.isConnected) {
      _ws.connect(userId);
      await Future.delayed(const Duration(milliseconds: 500));
    }

    _agentText.value = '';
    _state.value = AssistantState.recording;
    await _recorder.startRecording(_ws);
  }

  Future<void> stopRecording() async {
    await _recorder.stopRecording(_ws);
  }

  Future<void> sendText(String text) async {
    final userId = LocalDb.getUserId();
    if (userId == null) return;

    if (!_ws.isConnected) {
      _ws.connect(userId);
      await Future.delayed(const Duration(milliseconds: 500));
    }

    _messages.add(ChatMessage(role: 'user', content: text));
    _state.value = AssistantState.processing;
    _ws.sendTextMessage(text);
  }

  void confirmEvent(bool confirmed) {
    if (_pendingEvent.value != null) {
      final tempId =
          _pendingEvent.value!['temp_id'] ??
          _pendingEvent.value!['id']?.toString() ??
          '';
      _ws.sendEventConfirm(tempId, confirmed);

      if (confirmed) {
        final calCtrl = Get.find<CalendarController>();
        final id = _pendingEvent.value!['id'];
        if (id != null) {
          calCtrl.confirmEvent(id as int, true);
        }
      }
      _pendingEvent.value = null;
    }
  }

  void dismissPendingEvent() {
    _pendingEvent.value = null;
  }

  void clearMessages() {
    _messages.clear();
    _agentText.value = '';
    _asrPartial.value = '';
  }
}
