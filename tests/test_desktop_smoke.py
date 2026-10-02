import os
import sys
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from botty import actions
from botty.audio.tts import Speaker
from botty.config import Config
from botty.main import Botty


def test_desktop_app_starts_with_configured_window():
    app = Botty()
    try:
        assert app.screen.get_size() == (
            Config.DISPLAY_WIDTH,
            Config.DISPLAY_HEIGHT,
        )
        assert app.running
        assert app.speaker is not None
        assert app.brain is not None
    finally:
        pygame.quit()


def test_unknown_app_name_is_not_passed_to_a_shell(monkeypatch):
    def fail_to_launch(*args, **kwargs):
        raise AssertionError("unexpected process launch")

    monkeypatch.setattr(actions, "_search_exe", lambda name: None)
    monkeypatch.setattr(actions.subprocess, "Popen", fail_to_launch)

    result = actions.try_open_app("open notepad & whoami")

    assert result == "No encontre una aplicacion segura llamada notepad & whoami."


def test_speaker_initialization_does_not_require_a_network_request(monkeypatch, capsys):
    def unexpected_network_request():
        raise AssertionError("TTS initialization must not request voice data")

    monkeypatch.setitem(
        sys.modules,
        "edge_tts",
        SimpleNamespace(list_voices=unexpected_network_request),
    )
    speaker = Speaker()

    speaker.init()

    assert speaker._ready
    assert "Voz lista" in capsys.readouterr().out


def test_speaker_reports_playback_errors_and_resets_state(monkeypatch, capsys):
    speaker = Speaker()
    speaker._ready = True

    async def fail_to_play(_text):
        raise RuntimeError("audio device unavailable")

    monkeypatch.setattr(speaker, "_play", fail_to_play)
    speaker.say("Hola")
    speaker._worker.join(timeout=5)

    assert not speaker._worker.is_alive()
    assert not speaker.is_speaking()
    output = capsys.readouterr().out
    assert "[TTS] Botty: Hola" in output
    assert "audio device unavailable" in output
