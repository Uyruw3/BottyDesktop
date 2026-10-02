# Changelog

## 0.2.0.1

- Package Edge TTS in the Windows executable and keep its console visible.
- Remove the network request from voice initialization and report playback
  errors in the console.

## 0.2.0

- Published Botty Desktop from its own standalone repository.
- Clarified the Windows edition's optional voice and local AI setup.
- Added privacy notes for microphone, screen OCR, and desktop actions.

## 0.1.0

- Initial Windows desktop release.
- Added animated eyes, keyboard chat, and local conversation memory.
- Added optional microphone input, online speech synthesis, and local GGUF model
  support.
- Added Windows app launching, web search, and on-demand screen OCR.

## Known limitations

- Screen OCR requires Tesseract installed and available on `PATH`.
- Microphone input requires the optional PyAudio dependency.
- Voice recognition may send audio to Google's speech-recognition service.
- Local GGUF models and Tesseract are external and are not included in the
  release archive.
