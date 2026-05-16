import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';

class AudioPlayerService {
  final AudioPlayer _player = AudioPlayer();
  bool _isPlaying = false;
  final List<Uint8List> _buffer = [];

  bool get isPlaying => _isPlaying;

  AudioPlayerService() {
    _player.onPlayerComplete.listen((_) {
      _isPlaying = false;
    });
    _player.onPlayerStateChanged.listen((state) {
      if (state == PlayerState.completed || state == PlayerState.stopped) {
        _isPlaying = false;
      }
    });
  }

  void feed(Uint8List chunk) {
    _buffer.add(chunk);
  }

  Future<void> play() async {
    if (_buffer.isEmpty) return;
    _isPlaying = true;

    final combined = BytesBuilder();
    for (final chunk in _buffer) {
      combined.add(chunk);
    }
    _buffer.clear();

    try {
      await _player.play(BytesSource(combined.toBytes()));
    } catch (_) {
      _isPlaying = false;
    }
  }

  Future<void> stop() async {
    await _player.stop();
    _buffer.clear();
    _isPlaying = false;
  }

  void dispose() {
    _player.dispose();
  }
}
