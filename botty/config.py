import os


class Config:
    DISPLAY_WIDTH = 480
    DISPLAY_HEIGHT = 320
    FPS = 30

    TTS_ENGINE = os.getenv("TTS_ENGINE", "edge-tts")
    TTS_VOICE = os.getenv("TTS_VOICE", "es-MX-DaliaNeural")
    TTS_LANGUAGE = "es"

    EYE_COLOR = (60, 140, 230)
    BG_COLOR = (18, 18, 22)
