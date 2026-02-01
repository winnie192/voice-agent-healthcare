import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../config.dart';

class VoiceService {
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  final void Function(String base64Audio)? onAudioReceived;
  final void Function()? onDisconnected;
  bool _intentionalClose = false;
  bool _configSent = false;

  VoiceService({this.onAudioReceived, this.onDisconnected});

  bool get isConnected => _channel != null;

  Future<void> connect(String businessPhone, {int sampleRate = 48000}) async {
    _intentionalClose = false;
    _configSent = false;
    final uri =
        Uri.parse('${AppConfig.wsBaseUrl}/voice/browser-ws/$businessPhone');
    debugPrint('VoiceService: connecting to $uri');
    _channel = WebSocketChannel.connect(uri);

    try {
      await _channel!.ready;
      debugPrint('VoiceService: WebSocket ready, sending config (sampleRate=$sampleRate)');
      _channel!.sink.add(jsonEncode({
        'event': 'config',
        'sampleRate': sampleRate,
      }));
      _configSent = true;
    } catch (error) {
      debugPrint('VoiceService: WebSocket ready error: $error');
      return;
    }

    _subscription = _channel!.stream.listen(
      (message) {
        try {
          final data = jsonDecode(message as String) as Map<String, dynamic>;
          if (data['event'] == 'media') {
            final payload =
                (data['media'] as Map<String, dynamic>)['payload'] as String;
            onAudioReceived?.call(payload);
          }
        } catch (e) {
          debugPrint('VoiceService: error parsing message: $e');
        }
      },
      onDone: () {
        debugPrint('VoiceService: stream done (intentional=$_intentionalClose)');
        if (!_intentionalClose) {
          _cleanup();
          onDisconnected?.call();
        }
      },
      onError: (error) {
        debugPrint('VoiceService: stream error: $error');
        if (!_intentionalClose) {
          _cleanup();
          onDisconnected?.call();
        }
      },
    );
  }

  void sendAudio(String base64Audio) {
    if (_channel == null || !_configSent) return;
    try {
      _channel!.sink.add(jsonEncode({
        'event': 'media',
        'media': {'payload': base64Audio},
      }));
    } catch (e) {
      debugPrint('VoiceService: error sending audio: $e');
    }
  }

  void disconnect() {
    _intentionalClose = true;
    _channel?.sink.close();
    _cleanup();
  }

  void _cleanup() {
    _subscription?.cancel();
    _subscription = null;
    _channel = null;
  }
}
