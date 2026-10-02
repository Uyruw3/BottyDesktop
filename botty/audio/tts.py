import asyncio
import os
import queue
import tempfile
import threading

import pygame

from botty.config import Config


class Speaker:
    def __init__(self):
        self._queue = queue.Queue()
        self._worker = None
        self._is_speaking = False
        self._lock = threading.Lock()
        self._ready = False
        self._edge_tts_available = False

    def init(self):
        try:
            import edge_tts
            self._edge_tts_available = True
            self._ready = True
            print(f"  [TTS] Voz lista ({Config.TTS_VOICE}); se conecta al hablar.")
        except ImportError as e:
            print(f"  [TTS] Voz no disponible: no se pudo cargar edge-tts ({e})")

    def say(self, text, block=False):
        if not self._ready:
            print(f"  [TTS] No se puede reproducir la respuesta: {text}")
            return
        self._queue.put(text)
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._run, daemon=True)
            self._worker.start()
        if block:
            with self._lock:
                self._is_speaking = True
            while self._is_speaking:
                import time
                time.sleep(0.05)

    def _run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            try:
                text = self._queue.get(timeout=3)
            except queue.Empty:
                if self._queue.empty():
                    break
                continue
            with self._lock:
                self._is_speaking = True
            try:
                print(f"  [TTS] Botty: {text}")
                loop.run_until_complete(self._play(text))
            except Exception as e:
                print(f"  [TTS] Error al reproducir voz: {e}")
            finally:
                with self._lock:
                    self._is_speaking = False
        loop.close()

    async def _play(self, text):
        if not self._edge_tts_available:
            return
        import edge_tts
        communicate = edge_tts.Communicate(text, Config.TTS_VOICE)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_name = tmp.name
        tmp.close()
        try:
            await communicate.save(tmp_name)
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(tmp_name)
            pygame.mixer.music.play()
            print("  [TTS] Reproduciendo respuesta.")
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.05)
        except Exception as e:
            raise RuntimeError(
                "No se pudo generar o reproducir audio. Comprueba la conexión "
                "a Internet y la salida de sonido de Windows."
            ) from e
        finally:
            try:
                os.unlink(tmp_name)
            except Exception:
                pass

    def is_speaking(self):
        with self._lock:
            return self._is_speaking

    def stop(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        with self._lock:
            self._is_speaking = False
