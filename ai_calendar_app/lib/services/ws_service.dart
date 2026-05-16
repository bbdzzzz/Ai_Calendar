import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:get/get.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'local_db.dart';

typedef WsMessageHandler =
    void Function(String type, Map<String, dynamic> payload);
typedef WsBinaryHandler = void Function(Uint8List data);

class WsService extends GetxService {
  WebSocketChannel? _channel;
  final _isConnected = false.obs;
  StreamSubscription? _subscription;

  final List<WsMessageHandler> _msgHandlers = [];
  final List<WsBinaryHandler> _binHandlers = [];

  bool get isConnected => _isConnected.value;

  Future<WsService> init() async => this;

  void addMessageHandler(WsMessageHandler handler) => _msgHandlers.add(handler);
  void addBinaryHandler(WsBinaryHandler handler) => _binHandlers.add(handler);

  void connect(int userId) {
    if (_isConnected.value) return;

    LocalDb.getToken();
    final baseUrl = LocalDb.getServerUrl();
    final wsUrl = baseUrl.replaceFirst('http', 'ws');
    final uri = Uri.parse('$wsUrl/ws/$userId');

    _channel = WebSocketChannel.connect(uri);
    _isConnected.value = true;

    _subscription = _channel!.stream.listen(
      (data) {
        if (data is String) {
          try {
            final json = jsonDecode(data) as Map<String, dynamic>;
            final type = json['type'] as String? ?? '';
            final payload = json['payload'] as Map<String, dynamic>? ?? {};
            for (final h in _msgHandlers) {
              h(type, payload);
            }
          } catch (_) {}
        } else if (data is Uint8List) {
          for (final h in _binHandlers) {
            h(data);
          }
        }
      },
      onDone: () {
        _isConnected.value = false;
      },
      onError: (_) {
        _isConnected.value = false;
      },
    );
  }

  void sendJson(Map<String, dynamic> data) {
    _channel?.sink.add(jsonEncode(data));
  }

  void sendBinary(Uint8List data) {
    _channel?.sink.add(data);
  }

  void sendAudioStart() => sendJson({
    'type': 'audio_start',
    'payload': {'format': 'pcm', 'sample_rate': 16000},
  });
  void sendAudioEnd() => sendJson({'type': 'audio_end'});
  void sendTextMessage(String text) => sendJson({
    'type': 'text_message',
    'payload': {'text': text},
  });
  void sendEventConfirm(String tempId, bool confirmed) => sendJson({
    'type': 'event_confirm',
    'payload': {'temp_id': tempId, 'confirmed': confirmed},
  });

  void disconnect() {
    _subscription?.cancel();
    _channel?.sink.close();
    _isConnected.value = false;
  }

  @override
  void onClose() {
    disconnect();
    super.onClose();
  }
}
