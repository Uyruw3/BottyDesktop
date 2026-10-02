# Botty Desktop

Botty Desktop is the Windows desktop edition of Botty: an animated Pygame face
with local conversation memory, optional speech, and Windows app, web-search,
and screen-reading actions. The Raspberry Pi prototype is the physical edition
of the same Botty character; each edition has its own implementation and
installation.

**Standalone repository:** [Uyruw3/BottyDesktop](https://github.com/Uyruw3/BottyDesktop) ·
[Botty website](https://uyruw3.github.io/BottyTheRobot/) ·
[Robot edition](https://github.com/Uyruw3/BottyRobot)

## Requirements

- Windows 10 or newer
- Tesseract OCR installed and available on `PATH` for screen-reading actions
- Python 3.10 or newer only for installing from source

## Download for Windows

Download **Botty-Desktop-Windows-x64.exe** from the
[latest release](https://github.com/Uyruw3/BottyDesktop/releases/latest) and
open it. Python is not required. Tesseract is optional and only needed for
screen-reading; voice and local AI features have separate optional setup
requirements.

## Install and run

```powershell
cd BottyDesktop
python -m pip install -e ".[voice]"
botty
```

Speech recognition and online text-to-speech are optional. Install
`python -m pip install -e ".[microphone]"` to enable microphone input; Windows
may require a compatible PyAudio wheel. Local GGUF model support is available
with `python -m pip install -e ".[local-ai]"`; place the model in `botty/models/`.

To run tests:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

To build the standalone Windows executable from source:

```powershell
python -m pip install -e ".[dev]"
python -m PyInstaller --clean --noconfirm Botty-Desktop-Windows-x64.spec
```

## Privacy and safety

Screen-reading uses Tesseract on a screenshot captured only when requested.
Voice recognition may use Google's online speech service. Keep API keys and
personal model files out of source control. App-launch commands can start
programs on the Windows machine; review actions before enabling voice control.
