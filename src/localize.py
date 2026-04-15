from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import i18n

logger = logging.getLogger(__name__)

_FROZEN = getattr(sys, "_MEIPASS", None)
_BUNDLE_DIR = Path(_FROZEN) if _FROZEN else Path(__file__).parent
_LOCALES_DIR = _BUNDLE_DIR / "locales"

i18n.set("load_path", [str(_LOCALES_DIR)])
i18n.set("file_format", "yaml")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")
i18n.set("enable_memoization", True)
i18n.set("error_on_missing_translation", False)
i18n.set("error_on_missing_placeholder", False)


def _read_language_from_config() -> str:
    config_path = _BUNDLE_DIR / "config.json"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        lang = cfg.get("language", "en")
        if not isinstance(lang, str) or not lang.strip():
            return "en"
        return lang.strip().lower()
    except Exception:
        return "en"


_CURRENT_LOCALE = _read_language_from_config()
i18n.set("locale", _CURRENT_LOCALE)
logger.info("Locale set to '%s' (translations: %s)", _CURRENT_LOCALE, _LOCALES_DIR)

def t(key: str, **kwargs) -> str:
    return i18n.t(key, **kwargs)


def set_locale(lang: str) -> None:
    global _CURRENT_LOCALE
    _CURRENT_LOCALE = lang.strip().lower()
    i18n.set("locale", _CURRENT_LOCALE)
    logger.info("Locale changed to '%s'", _CURRENT_LOCALE)


def get_locale() -> str:
    return _CURRENT_LOCALE
