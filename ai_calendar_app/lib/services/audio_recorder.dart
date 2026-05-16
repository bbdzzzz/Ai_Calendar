import 'dart:async';
import 'dart:typed_data';

import 'package:record/record.dart';
import 'ws_service.dart';

class AudioRecorderService {
  final AudioRecorder _recorder = AudioRecorder();
  StreamSubscription<RecordState>? _stateSub;
  StreamSubscription<Uint8List>? _streamSub;
  bool _isRecording = false;

  bool get isRecording => _isRecording;

  Future<bool> hasPermission() => _recorder.hasPermission();

  Future<void> startRecording(WsService ws) async {
    if (_isRecording) return;

    final hasPerm = await _recorder.hasPermission();
    if (!hasPerm) return;

    ws.sendAudioStart();

    final stream = await _recorder.startStream(
      const RecordConfig(
        encoder: AudioEncoder.pcm16bits,
        sampleRate: 16000,
        numChannels: 1,
      ),
    );

    _isRecording = true;

    _streamSub = stream.listen((data) {
      ws.sendBinary(data);
    });

    _stateSub = _recorder.onStateChanged().listen((state) {
      if (state == RecordState.stop) {
        _isRecording = false;
      }
    });
  }

  Future<void> stopRecording(WsService ws) async {
    if (!_isRecording) return;

    await _streamSub?.cancel();
    _streamSub = null;
    await _stateSub?.cancel();
    _stateSub = null;

    await _recorder.stop();
    _isRecording = false;
    ws.sendAudioEnd();
  }

  void dispose() {
    _streamSub?.cancel();
    _stateSub?.cancel();
    _recorder.dispose();
  }
}
