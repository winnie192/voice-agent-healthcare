import 'dart:async';
import 'dart:convert';
import 'dart:js_interop';
import 'dart:typed_data';

import 'package:web/web.dart' as web;

const List<int> _ulawToLinearTable = [
  -32124, -31100, -30076, -29052, -28028, -27004, -25980, -24956,
  -23932, -22908, -21884, -20860, -19836, -18812, -17788, -16764,
  -15996, -15484, -14972, -14460, -13948, -13436, -12924, -12412,
  -11900, -11388, -10876, -10364,  -9852,  -9340,  -8828,  -8316,
   -7932,  -7676,  -7420,  -7164,  -6908,  -6652,  -6396,  -6140,
   -5884,  -5628,  -5372,  -5116,  -4860,  -4604,  -4348,  -4092,
   -3900,  -3772,  -3644,  -3516,  -3388,  -3260,  -3132,  -3004,
   -2876,  -2748,  -2620,  -2492,  -2364,  -2236,  -2108,  -1980,
   -1884,  -1820,  -1756,  -1692,  -1628,  -1564,  -1500,  -1436,
   -1372,  -1308,  -1244,  -1180,  -1116,  -1052,   -988,   -924,
    -876,   -844,   -812,   -780,   -748,   -716,   -684,   -652,
    -620,   -588,   -556,   -524,   -492,   -460,   -428,   -396,
    -372,   -356,   -340,   -324,   -308,   -292,   -276,   -260,
    -244,   -228,   -212,   -196,   -180,   -164,   -148,   -132,
    -120,   -112,   -104,    -96,    -88,    -80,    -72,    -64,
     -56,    -48,    -40,    -32,    -24,    -16,     -8,      0,
   32124,  31100,  30076,  29052,  28028,  27004,  25980,  24956,
   23932,  22908,  21884,  20860,  19836,  18812,  17788,  16764,
   15996,  15484,  14972,  14460,  13948,  13436,  12924,  12412,
   11900,  11388,  10876,  10364,   9852,   9340,   8828,   8316,
    7932,   7676,   7420,   7164,   6908,   6652,   6396,   6140,
    5884,   5628,   5372,   5116,   4860,   4604,   4348,   4092,
    3900,   3772,   3644,   3516,   3388,   3260,   3132,   3004,
    2876,   2748,   2620,   2492,   2364,   2236,   2108,   1980,
    1884,   1820,   1756,   1692,   1628,   1564,   1500,   1436,
    1372,   1308,   1244,   1180,   1116,   1052,    988,    924,
     876,    844,    812,    780,    748,    716,    684,    652,
     620,    588,    556,    524,    492,    460,    428,    396,
     372,    356,    340,    324,    308,    292,    276,    260,
     244,    228,    212,    196,    180,    164,    148,    132,
     120,    112,    104,     96,     88,     80,     72,     64,
      56,     48,     40,     32,     24,     16,      8,      0,
];

class WebAudioService {
  web.MediaStream? _mediaStream;
  web.AudioContext? _captureContext;
  web.AudioContext? _playbackContext;
  double _playbackTime = 0;
  final void Function(String base64Pcm)? onAudioCaptured;
  bool _capturing = false;
  int sampleRate = 48000;

  WebAudioService({this.onAudioCaptured});

  Future<bool> requestMicPermission() async {
    try {
      final constraints = web.MediaStreamConstraints(
        audio: true.toJS,
        video: false.toJS,
      );
      _mediaStream =
          await web.window.navigator.mediaDevices.getUserMedia(constraints).toDart;
      return true;
    } catch (e) {
      return false;
    }
  }

  void startCapture() {
    if (_mediaStream == null || _capturing) return;
    _capturing = true;

    _captureContext = web.AudioContext();
    _playbackContext = web.AudioContext();
    _playbackTime = 0;

    sampleRate = _captureContext!.sampleRate.toInt();

    final source = _captureContext!.createMediaStreamSource(_mediaStream!);
    final processor = _captureContext!.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (web.AudioProcessingEvent event) {
      if (!_capturing) return;
      final inputBuffer = event.inputBuffer;
      final channelData = inputBuffer.getChannelData(0);
      final float32List = channelData.toDart;

      final pcm16 = _float32ToPcm16(float32List);
      final b64 = base64Encode(pcm16.buffer.asUint8List());
      onAudioCaptured?.call(b64);
    }.toJS;

    source.connect(processor);
    processor.connect(_captureContext!.destination);
  }

  void stopCapture() {
    _capturing = false;
    _captureContext?.close();
    _captureContext = null;
    _mediaStream?.getTracks().toDart.forEach((track) => track.stop());
    _mediaStream = null;
  }

  void playAudioChunk(String base64Audio) {
    _playbackContext ??= web.AudioContext();
    final bytes = base64Decode(base64Audio);

    final float32 = Float32List(bytes.length);
    for (var i = 0; i < bytes.length; i++) {
      float32[i] = _ulawToLinearTable[bytes[i]] / 32768.0;
    }

    final buffer = _playbackContext!.createBuffer(1, float32.length, 8000);
    buffer.getChannelData(0).toDart.setAll(0, float32);

    final source = _playbackContext!.createBufferSource();
    source.buffer = buffer;
    source.connect(_playbackContext!.destination);

    final now = _playbackContext!.currentTime;
    if (_playbackTime < now) _playbackTime = now;
    source.start(_playbackTime);
    _playbackTime += float32.length / 8000;
  }

  void dispose() {
    stopCapture();
    _playbackContext?.close();
    _playbackContext = null;
  }

  Int16List _float32ToPcm16(List<double> float32) {
    final pcm = Int16List(float32.length);
    for (var i = 0; i < float32.length; i++) {
      final s = float32[i].clamp(-1.0, 1.0);
      pcm[i] = (s * 32767).round();
    }
    return pcm;
  }

  Uint8List _downsample(Int16List input, num fromRate, int toRate) {
    if (fromRate == toRate) {
      return input.buffer.asUint8List();
    }

    // Apply a simple moving-average low-pass filter before decimation
    // to prevent aliasing. Window size = decimation ratio rounded up.
    final ratio = fromRate.toDouble() / toRate;
    final windowSize = ratio.ceil();

    // Running-sum low-pass filter
    final filtered = Int16List(input.length);
    double runningSum = 0;
    for (var i = 0; i < input.length; i++) {
      runningSum += input[i];
      if (i >= windowSize) {
        runningSum -= input[i - windowSize];
      }
      final count = i < windowSize ? (i + 1) : windowSize;
      filtered[i] = (runningSum / count).round();
    }

    // Decimate with linear interpolation
    final newLength = (input.length / ratio).floor();
    final output = Int16List(newLength);
    for (var i = 0; i < newLength; i++) {
      final srcPos = i * ratio;
      final idx = srcPos.floor();
      final frac = srcPos - idx;
      if (idx + 1 < filtered.length) {
        output[i] =
            (filtered[idx] * (1.0 - frac) + filtered[idx + 1] * frac).round();
      } else {
        output[i] = filtered[idx.clamp(0, filtered.length - 1)];
      }
    }
    return output.buffer.asUint8List();
  }
}
