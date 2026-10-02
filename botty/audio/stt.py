"""
Speech-to-Text module — escucha y transcribe voz.
Soporta speech_recognition (Google), Whisper local, Vosk y Azure.
"""

import time
import queue
import threading
import numpy as np
from botty.config import Config


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self._init_done = False
        self._audio_queue = queue.Queue()
        self._listening = False
        self._listener_thread = None

    def init(self):
        if self._init_done:
            return
        self._init_done = True
        engine = Config.STT_ENGINE
        if engine == "whisper":
            self._init_whisper()
        elif engine == "vosk":
            self._init_vosk()
        elif engine == "azure":
            self._init_azure()
        else:
            self._init_speech_recognition()

    def _init_speech_recognition(self):
        try:
            import speech_recognition as sr
        except ImportError:
            print("  [STT] SpeechRecognition no instalado")
            return
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = Config.VOICE_ACTIVATION_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        try:
            self.microphone = sr.Microphone(device_index=Config.MIC_DEVICE_INDEX)
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"  [STT] SpeechRecognition listo (microfono: {self.microphone.device_index})")
        except Exception as e:
            print(f"  [STT] Error iniciando microfono: {e}")
            self.microphone = None

    def _init_whisper(self):
        try:
            import whisper
            model_name = getattr(Config, "WHISPER_MODEL", "base")
            self.recognizer = whisper.load_model(model_name)
            print(f"  [STT] Whisper cargado (modelo: {model_name})")
        except ImportError:
            print("  [STT] Whisper no instalado. pip install openai-whisper")
            self.recognizer = None

    def _init_vosk(self):
        try:
            from vosk import Model, KaldiRecognizer
            model_path = getattr(Config, "VOSK_MODEL_PATH", "~/.botty/vosk-model")
            import os
            model_path = os.path.expanduser(model_path)
            if os.path.exists(model_path):
                self.recognizer = KaldiRecognizer(Model(model_path), 16000)
                print(f"  [STT] Vosk cargado desde {model_path}")
            else:
                print(f"  [STT] Modelo Vosk no encontrado en {model_path}")
                self.recognizer = None
        except ImportError:
            print("  [STT] Vosk no instalado. pip install vosk")
            self.recognizer = None

    def _init_azure(self):
        try:
            import azure.cognitiveservices.speech as speechsdk
            key = getattr(Config, "AZURE_SPEECH_KEY", "")
            region = getattr(Config, "AZURE_SPEECH_REGION", "eastus")
            if key:
                config = speechsdk.SpeechConfig(subscription=key, region=region)
                config.speech_recognition_language = Config.STT_LANGUAGE
                self.recognizer = speechsdk.SpeechRecognizer(speech_config=config)
                print("  [STT] Azure Speech listo")
            else:
                print("  [STT] Azure Speech: falta API key")
                self.recognizer = None
        except ImportError:
            print("  [STT] Azure SDK no instalado")
            self.recognizer = None

    def listen(self, timeout: float = 5.0, phrase_limit: float = 8.0) -> str | None:
        if not self._init_done or self.recognizer is None:
            return None
        engine = Config.STT_ENGINE
        if engine == "whisper":
            return self._listen_whisper(timeout)
        elif engine == "vosk":
            return self._listen_vosk(timeout)
        elif engine == "azure":
            return self._listen_azure(timeout)
        return self._listen_speech_recognition(timeout, phrase_limit)

    def _listen_speech_recognition(self, timeout: float, phrase_limit: float) -> str | None:
        import speech_recognition as sr
        if self.microphone is None:
            return None
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"  [STT] Error escuchando: {e}")
            return None
        try:
            text = self.recognizer.recognize_google(audio, language=Config.STT_LANGUAGE)
            return text.lower()
        except (sr.UnknownValueError, sr.RequestError) as e:
            print(f"  [STT] Error de reconocimiento: {e}")
            return None

    def _listen_whisper(self, timeout: float) -> str | None:
        try:
            import pyaudio
        except ImportError:
            print("  [STT] pyaudio no instalado")
            return None
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                          input=True, frames_per_buffer=CHUNK)
        except Exception as e:
            print(f"  [STT] Error abriendo stream: {e}")
            p.terminate()
            return None
        frames = []
        start = time.time()
        silent_chunks = 0
        max_silent_chunks = int(RATE / CHUNK * 1.5)
        while time.time() - start < timeout:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                volume = np.abs(audio_data).mean()
                if volume < Config.VOICE_ACTIVATION_THRESHOLD:
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                if silent_chunks > max_silent_chunks and len(frames) > 20:
                    break
            except Exception as e:
                print(f"  [STT] Error leyendo audio: {e}")
                break
        stream.stop_stream()
        stream.close()
        p.terminate()
        if len(frames) < 10:
            return None
        audio_np = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32) / 32768.0
        result = self.recognizer.transcribe(audio_np, language=Config.STT_LANGUAGE.split("-")[0] or "es")
        text = result.get("text", "").strip().lower()
        return text if text else None

    def _listen_vosk(self, timeout: float) -> str | None:
        try:
            import pyaudio
            import json
        except ImportError:
            return None
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=8000)
        start = time.time()
        frames = []
        while time.time() - start < timeout:
            data = stream.read(4000, exception_on_overflow=False)
            frames.append(data)
            vol = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            if np.abs(vol).mean() < 200:
                time.sleep(0.1)
            if len(frames) > 50:
                break
        stream.stop_stream()
        stream.close()
        p.terminate()
        audio_data = b"".join(frames)
        if self.recognizer.AcceptWaveform(audio_data, len(audio_data)):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "").lower()
        return None

    def _listen_azure(self, timeout: float) -> str | None:
        try:
            result = self.recognizer.recognize_once()
            if result.reason.name == "RecognizedSpeech":
                return result.text.lower()
        except Exception as e:
            print(f"  [STT] Azure error: {e}")
        return None

    def start_continuous_listener(self, callback):
        """Inicia un hilo que escucha continuamente y llama a callback con texto."""
        self._listening = True
        def _loop():
            while self._listening:
                try:
                    text = self.listen(timeout=2.0)
                    if text:
                        callback(text)
                except Exception as e:
                    print(f"  [STT] Listener error: {e}")
                time.sleep(0.1)
        self._listener_thread = threading.Thread(target=_loop, daemon=True)
        self._listener_thread.start()

    def stop_continuous_listener(self):
        self._listening = False
        if self._listener_thread:
            self._listener_thread.join(timeout=2)
