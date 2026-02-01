import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/business_provider.dart';
import '../services/voice_service.dart';
import '../services/web_audio_service.dart';
import '../widgets/app_drawer.dart';

class VoiceCallScreen extends StatefulWidget {
  const VoiceCallScreen({super.key});

  @override
  State<VoiceCallScreen> createState() => _VoiceCallScreenState();
}

class _VoiceCallScreenState extends State<VoiceCallScreen> {
  VoiceService? _voiceService;
  WebAudioService? _audioService;
  bool _connected = false;
  bool _micGranted = false;
  int _seconds = 0;
  Timer? _timer;
  int _sentChunks = 0;
  int _receivedChunks = 0;
  String _status = 'Tap to call';

  Future<void> _toggleCall() async {
    if (_connected) {
      _disconnect();
    } else {
      await _connect();
    }
  }

  Future<void> _connect() async {
    final phone = context.read<BusinessProvider>().business?.phone;
    if (phone == null) {
      setState(() => _status = 'No business phone found');
      return;
    }

    setState(() => _status = 'Requesting mic access...');

    _audioService = WebAudioService(
      onAudioCaptured: (base64Pcm) {
        _voiceService?.sendAudio(base64Pcm);
        if (mounted) setState(() => _sentChunks++);
      },
    );

    _micGranted = await _audioService!.requestMicPermission();
    if (!_micGranted) {
      setState(() => _status = 'Mic permission denied');
      return;
    }

    setState(() => _status = 'Connecting...');

    _voiceService = VoiceService(
      onAudioReceived: (audio) {
        _audioService?.playAudioChunk(audio);
        if (mounted) setState(() => _receivedChunks++);
      },
      onDisconnected: () {
        if (mounted) _disconnect();
      },
    );
    _audioService!.startCapture();
    await _voiceService!.connect(phone, sampleRate: _audioService!.sampleRate);

    setState(() {
      _connected = true;
      _seconds = 0;
      _sentChunks = 0;
      _receivedChunks = 0;
      _status = 'Connected - Listening...';
    });
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted) setState(() => _seconds++);
    });
  }

  void _disconnect() {
    _audioService?.stopCapture();
    _audioService?.dispose();
    _voiceService?.disconnect();
    _timer?.cancel();
    if (mounted) {
      setState(() {
        _connected = false;
        _voiceService = null;
        _audioService = null;
        _status = 'Call ended';
      });
    }
  }

  String get _formattedTime {
    final m = (_seconds ~/ 60).toString().padLeft(2, '0');
    final s = (_seconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  void dispose() {
    _audioService?.stopCapture();
    _audioService?.dispose();
    _voiceService?.disconnect();
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Voice Call')),
      drawer: const AppDrawer(),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_formattedTime,
                style: Theme.of(context).textTheme.displayMedium),
            const SizedBox(height: 8),
            Text(_status, style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: 32),
            FloatingActionButton.large(
              onPressed: _toggleCall,
              backgroundColor: _connected ? Colors.red : Colors.green,
              child: Icon(_connected ? Icons.call_end : Icons.mic, size: 36),
            ),
            if (_connected) ...[
              const SizedBox(height: 24),
              Text('Mic chunks sent: $_sentChunks',
                  style: Theme.of(context).textTheme.bodySmall),
              Text('Audio chunks received: $_receivedChunks',
                  style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }
}
