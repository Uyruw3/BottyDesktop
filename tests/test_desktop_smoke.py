import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from botty import actions
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
