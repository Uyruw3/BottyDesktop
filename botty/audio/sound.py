"""
Sound utilities — efectos de sonido, generacion de tonos y audio.
Incluye sintetizador simple y reproduccion de archivos.
"""

import time
import math
import struct
import threading
import wave
import tempfile
import os


class SoundGenerator:
    """Genera tonos y efectos de sonido simples usando Pygame."""
    def __init__(self):
        self._initialized = False
        self._volume = 0.5
        self._sample_rate = 22050
        self._lock = threading.Lock()

    def init(self):
        if self._initialized:
            return
        try:
            import pygame
            pygame.mixer.init(frequency=self._sample_rate, size=-16, channels=1, buffer=512)
            self._initialized = True
        except Exception as e:
            print(f"  [Sound] Init error: {e}")

    def _generate_tone(self, frequency: float, duration: float, volume: float = None) -> bytes:
        vol = (volume if volume is not None else self._volume) * 0.5
        n_samples = int(self._sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self._sample_rate
            value = int(32767 * vol * math.sin(2 * math.pi * frequency * t))
            samples.append(value)
        return struct.pack(f"<{n_samples}h", *samples)

    def _generate_sweep(self, freq_start: float, freq_end: float, duration: float) -> bytes:
        n_samples = int(self._sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self._sample_rate
            frac = i / n_samples
            freq = freq_start + (freq_end - freq_start) * frac
            value = int(32767 * self._volume * 0.4 * math.sin(2 * math.pi * freq * t))
            samples.append(value)
        return struct.pack(f"<{n_samples}h", *samples)

    def _generate_noise(self, duration: float, volume: float = None) -> bytes:
        import random
        vol = (volume if volume is not None else self._volume) * 0.3
        n_samples = int(self._sample_rate * duration)
        samples = [int(32767 * vol * (random.random() * 2 - 1)) for _ in range(n_samples)]
        return struct.pack(f"<{n_samples}h", *samples)

    def _play_wav(self, wav_data: bytes):
        if not self._initialized:
            return
        import pygame
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(wav_data)
            tmp_path = f.name
        try:
            sound = pygame.mixer.Sound(tmp_path)
            sound.set_volume(self._volume)
            sound.play()
        except Exception as e:
            print(f"  [Sound] Play error: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def play_tone(self, frequency: float, duration: float):
        wav_data = self._generate_tone(frequency, duration)
        self._play_wav(wav_data)

    def play_beep(self):
        self.play_tone(800, 0.1)

    def play_double_beep(self):
        self.play_tone(600, 0.08)
        time.sleep(0.08)
        self.play_tone(800, 0.08)

    def play_success(self):
        wav_data = self._generate_tone(523, 0.1)
        wav_data += self._generate_tone(659, 0.1)
        wav_data += self._generate_tone(784, 0.15)
        self._play_wav(wav_data)

    def play_error(self):
        wav_data = self._generate_tone(200, 0.2)
        wav_data += self._generate_tone(150, 0.3)
        self._play_wav(wav_data)

    def play_notification(self):
        self.play_tone(1000, 0.05)
        time.sleep(0.05)
        self.play_tone(1200, 0.05)

    def play_alarm(self, duration: float = 1.0):
        n_cycles = int(duration / 0.5)
        wav_data = b""
        for _ in range(n_cycles):
            wav_data += self._generate_tone(880, 0.2)
            wav_data += self._generate_silence(0.1)
            wav_data += self._generate_tone(660, 0.2)
        self._play_wav(wav_data)

    def play_sweep(self, freq_start: float, freq_end: float, duration: float):
        wav_data = self._generate_sweep(freq_start, freq_end, duration)
        self._play_wav(wav_data)

    def play_noise(self, duration: float):
        wav_data = self._generate_noise(duration)
        self._play_wav(wav_data)

    def play_robot_talk(self, duration: float = 0.5):
        """Simula el sonido de un robot hablando."""
        wav_data = self._generate_noise(duration * 0.3, 0.2)
        wav_data += self._generate_tone(400, duration * 0.4)
        wav_data += self._generate_noise(duration * 0.3, 0.15)
        self._play_wav(wav_data)

    def play_startup(self):
        wav_data = self._generate_sweep(200, 1000, 0.3)
        wav_data += self._generate_sweep(1000, 1500, 0.2)
        wav_data += self._generate_tone(1200, 0.3)
        self._play_wav(wav_data)

    def play_shutdown(self):
        wav_data = self._generate_sweep(1000, 100, 0.5)
        self._play_wav(wav_data)

    def _generate_silence(self, duration: float) -> bytes:
        n_samples = int(self._sample_rate * duration)
        return struct.pack(f"<{n_samples}h", *([0] * n_samples))

    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))

    def get_volume(self) -> float:
        return self._volume

    def cleanup(self):
        if self._initialized:
            try:
                import pygame
                pygame.mixer.quit()
            except Exception:
                pass
            self._initialized = False
