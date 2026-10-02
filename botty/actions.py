import os
import random
import re
import shutil
import subprocess
import urllib.parse
import webbrowser
from pathlib import Path

import mss
import pytesseract
from PIL import Image

def _search_exe(name):
    if not name or Path(name).name.lower() != name.lower():
        return None

    found = shutil.which(name)
    if found:
        print(f"  [Buscar] encontrado: {found}")
        return Path(found)

    quick = [
        Path(os.environ["WINDIR"]) / "System32",
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps",
    ]
    for d in quick:
        if not d or not d.exists():
            continue
        p = d / f"{name}.exe"
        if p.exists():
            print(f"  [Buscar] encontrado: {p}")
            return p.resolve()

    print(f"  [Buscar] no se encontro: {name}")
    return None


def _open_url(url):
    webbrowser.open(url)


def try_open_app(text):
    m = re.match(r"^(abre|abrir|open|lanza|lanzar|ejecuta|ejecutar|inicia|iniciar)\s+(.+)$", text.strip(), re.I)
    if not m:
        return None

    raw_name = m.group(2).strip()
    app_name = raw_name.lower()
    app_name = re.sub(r"^(el|la|un|una|lo|los|las)\s+", "", app_name)
    print(f"  [Accion] intentando abrir: {app_name}")

    ALIASES = {
        "bloc de notas": "notepad",
        "bloc": "notepad",
        "calc": "calc",
        "calculadora": "calc",
        "cmd": "cmd",
        "simbolo del sistema": "cmd",
        "terminal": "cmd",
        "powershell": "powershell",
        "explorer": "explorer",
        "explorador de archivos": "explorer",
        "explorador": "explorer",
        "configuracion": "ms-settings:",
        "settings": "ms-settings:",
        "edge": "microsoft-edge:",
        "firefox": "firefox",
        "bottydesktop": str(Path(__file__).parent.parent),
        "botty desktop": str(Path(__file__).parent.parent),
    }
    phrases = ["Abriendo", "Voy a abrir", "Ahi va", "Lanzando", "Te abro"]

    if app_name in ALIASES:
        target = ALIASES[app_name]
        print(f"  [Accion] alias -> start {target}")
        if ":" in target or Path(target).exists():
            os.startfile(target)
            return f"{random.choice(phrases)} {raw_name}!"
        exe = _search_exe(target)
        if exe:
            subprocess.Popen([str(exe)])
            return f"{random.choice(phrases)} {raw_name}!"
        return f"No encontre la aplicacion {raw_name}."

    exe = _search_exe(app_name)
    if exe:
        print(f"  [Accion] lanzando: {exe}")
        subprocess.Popen([str(exe)])
        return f"{random.choice(phrases)} {raw_name}!"

    return f"No encontre una aplicacion segura llamada {raw_name}."


def _detect_city():
    try:
        import json, urllib.request
        with urllib.request.urlopen("http://ip-api.com/json/?fields=city", timeout=3) as r:
            data = json.loads(r.read().decode())
            return data.get("city", "")
    except Exception:
        return ""


def try_weather(text):
    m = re.search(r"(clima|tiempo|weather|temperatura)", text, re.I)
    if not m:
        return None

    city_match = re.search(r"(?:en|de|del)\s+(.+)", text, re.I)
    try:
        import urllib.request
        if city_match:
            city = city_match.group(1).strip()
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C:+%t,+humedad+%h&lang=es"
        else:
            city = _detect_city()
            if not city:
                return "No pude detectar tu ubicacion."
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C:+%t,+humedad+%h&lang=es"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = resp.read().decode("utf-8").strip()
        if data:
            print(f"  [Clima] {city}: {data}")
            return f"En {city} hay {data}"
    except Exception as e:
        print(f"  [Clima] Error: {e}")
        return None


def try_web_search(text):
    m = re.match(r"^(busca|buscar|search|googlea|googlear|investiga|investigar)\s+(.+)$", text.strip(), re.I)
    if not m:
        return None

    query = m.group(2).strip()
    print(f"  [Buscar] buscando en internet: {query}")
    encoded = urllib.parse.quote_plus(query)
    _open_url(f"https://www.google.com/search?q={encoded}")
    return f"Buscando {query} en internet!"


def try_read_desktop(text):
    if not re.search(r"(leer|lista|listame|que hay|muestrame|como esta)\s+(mi\s+)?escritorio", text, re.I):
        return None

    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        return "No encontre tu escritorio."

    items = []
    try:
        for f in desktop.iterdir():
            label = f.name
            if f.is_dir():
                label += " (carpeta)"
            items.append(label)
    except Exception:
        pass

    if not items:
        return "Tu escritorio esta vacio."

    parts = items[:10]
    if len(items) > 10:
        parts.append(f"y {len(items)-10} mas")
    return f"En tu escritorio hay: {', '.join(parts)}"


def try_read_screen(text):
    patterns = [
        r"(qué|que)\s*ves",
        r"lee\s+(la\s+)?pantalla",
        r"qué\s+(hay|texto|dice|pon(e|drá))\s+(en\s+)?(la\s+)?pantalla",
        r"describe\s+(la\s+)?pantalla",
        r"qué\s+puedes\s+ver",
        r"puedes\s+ver",
        r"ves\s+algo",
        r"captura\s+(la\s+)?pantalla",
        r"que\s+(hay|dice|pone|texto)",
    ]
    if not any(re.search(p, text, re.I) for p in patterns):
        return None

    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        ocr_text = pytesseract.image_to_string(img, lang="spa").strip()
        if not ocr_text:
            return "No veo texto en la pantalla."
        print(f"  [OCR] Detectado: {ocr_text[:200]}")
        reply = ocr_text[:500]
        return f"En la pantalla veo: {reply}"
    except Exception as e:
        print(f"  [OCR] Error: {e}")
        return "No pude leer la pantalla."
