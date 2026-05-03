from __future__ import annotations

import json
import sys
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, QLocale


# code ISO -> nom natif affiché dans le combo
LANGUAGES = {
    "fr": "Français",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "it": "Italiano",
    "ja": "日本語",
    "ko": "한국어",
    "ru": "Русский",
    "zh": "中文",
}


def _locales_dir() -> Path:
    """Renvoie le dossier des fichiers JSON. Compatible PyInstaller :
    en mode frozen, les ressources sont sous ``sys._MEIPASS``."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        # On essaie plusieurs emplacements possibles selon le spec d'inclusion.
        for candidate in (base / "locales", base / "wizard" / "locales"):
            if candidate.is_dir():
                return candidate
    return Path(__file__).resolve().parents[1] / "locales"


LOCALES_DIR = _locales_dir()

# Cache des tables chargées : {code: {key: str}}
_cache: dict[str, dict[str, str]] = {}


def _load(code: str) -> dict[str, str]:
    if code in _cache:
        return _cache[code]
    path = LOCALES_DIR / f"{code}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, json.JSONDecodeError):
        data = {}
    _cache[code] = data
    return data


class _Signaler(QObject):
    language_changed = pyqtSignal(str)


signaler = _Signaler()
current_lang = "fr"


def detect_system_language() -> str:
    """Renvoie le code ISO le mieux assorti à la langue d'interface
    Windows, ou 'en' en dernier recours.

    Ordre de préférence :
      1. GetUserDefaultUILanguage (langue d'AFFICHAGE Windows, pas le
         format régional — c'est ce que l'utilisateur attend).
      2. QLocale.system().uiLanguages() (liste ordonnée de Qt).
      3. QLocale.system().name() (format régional, dernier recours).
    """
    # 1) API Windows : LCID -> langue primaire (10 bits de poids faible).
    if sys.platform == "win32":
        try:
            import ctypes
            lcid = int(ctypes.windll.kernel32.GetUserDefaultUILanguage())
            primary = lcid & 0x3FF
            # Voir : https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/
            primary_map = {
                0x09: "en", 0x0c: "fr", 0x07: "de", 0x0a: "es",
                0x10: "it", 0x11: "ja", 0x12: "ko", 0x19: "ru",
                0x04: "zh",
            }
            code = primary_map.get(primary)
            if code in LANGUAGES:
                return code
        except Exception:
            pass

    # 2) Liste ordonnée fournie par Qt (ex: ['en-US', 'fr-FR']).
    try:
        for lang in QLocale.system().uiLanguages():
            code = lang.split("-", 1)[0].lower()
            if code in LANGUAGES:
                return code
    except Exception:
        pass

    # 3) Format régional.
    try:
        name = QLocale.system().name()
        code = name.split("_", 1)[0].lower()
        if code in LANGUAGES:
            return code
    except Exception:
        pass

    return "en"


def set_language(code: str) -> None:
    global current_lang
    if code not in LANGUAGES:
        code = "en"
    if code == current_lang:
        return
    current_lang = code
    signaler.language_changed.emit(code)


def tr(key: str, **kwargs) -> str:
    """Renvoie la chaîne traduite. Fallback : anglais, puis la clé brute."""
    s = _load(current_lang).get(key)
    if s is None:
        s = _load("en").get(key, key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s
