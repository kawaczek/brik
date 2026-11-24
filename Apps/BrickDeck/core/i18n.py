"""
BrickDeck i18n (Internationalization) Engine
Supports multi-language UI, fallback to English, system locale auto-detection,
and JSON locale packs in Apps/BrickDeck/locales/*.json.
"""

import os
import json
import glob
from typing import Dict, Any, Optional, List


LANGUAGE_ALIASES = {
    # Polish
    "pl": "pl", "pol": "pl", "polish": "pl", "polski": "pl",
    # English
    "en": "en", "eng": "en", "english": "en", "angielski": "en",
    # German
    "de": "de", "ger": "de", "deu": "de", "deutsch": "de", "german": "de", "niemiecki": "de",
    # Spanish
    "es": "es", "spa": "es", "espanol": "es", "español": "es", "spanish": "es", "hiszpanski": "es",
    # French
    "fr": "fr", "fre": "fr", "fra": "fr", "francais": "fr", "français": "fr", "french": "fr",
    # Italian
    "it": "it", "ita": "it", "italiano": "it", "italian": "it",
    # Chinese
    "zh": "zh", "chi": "zh", "zho": "zh", "chinese": "zh", "zhongwen": "zh",
    # Japanese
    "ja": "ja", "jp": "ja", "jpn": "ja", "japanese": "ja",
    # Korean
    "ko": "ko", "kor": "ko", "korean": "ko",
    # Russian
    "ru": "ru", "rus": "ru", "russian": "ru",
    # Portuguese
    "pt": "pt", "por": "pt", "portuguese": "pt", "portugues": "pt",
}

# TrimUI system configuration candidates on SD Card and internal storage
TRIMUI_CANDIDATE_PATHS = [
    "/mnt/SDCARD/trimui/system/language",
    "/mnt/SDCARD/trimui/system/language.json",
    "/mnt/SDCARD/trimui/system/system.json",
    "/mnt/SDCARD/trimui/app/system/system.json",
    "/mnt/SDCARD/System/etc/language.json",
    "/mnt/SDCARD/System/state/language",
    "/mnt/SDCARD/System/state/language.json",
    "/mnt/SDCARD/System/system.json",
    "/mnt/UDISK/language",
    "/mnt/UDISK/system.json",
    "/mnt/UDISK/trimui/system/language.json",
    "/etc/trimui/language",
    "/etc/trimui/language.json",
    "/etc/language",
    "/etc/language.json",
]


class I18nManager:
    """Manages translations and locale switching for BrickDeck OS."""

    def __init__(self, locales_dir: Optional[str] = None):
        if locales_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            locales_dir = os.path.join(base_dir, "locales")
        self.locales_dir = locales_dir
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.active_locale = "en"
        self.fallback_locale = "en"
        self.is_auto = True
        self.available_locales: List[Dict[str, str]] = []

        self.load_all_locales()
        self.init_from_config()

    def _normalize_lang_code(self, raw: Any) -> Optional[str]:
        """Convert raw language identifier, string, or alias into ISO code."""
        if not raw:
            return None
        if isinstance(raw, int):
            return None
        raw_str = str(raw).strip().lower()
        if not raw_str:
            return None

        # Check full string alias (e.g. "polish", "deutsch")
        if raw_str in LANGUAGE_ALIASES:
            return LANGUAGE_ALIASES[raw_str]

        # Check prefixed code (e.g. "pl_PL.UTF-8" -> "pl", "en-US" -> "en")
        for delimiter in (".", "_", "-", "/", " "):
            raw_str = raw_str.split(delimiter)[0]
            if raw_str in LANGUAGE_ALIASES:
                return LANGUAGE_ALIASES[raw_str]

        return LANGUAGE_ALIASES.get(raw_str, raw_str if len(raw_str) == 2 else None)

    def load_all_locales(self):
        """Scan locales_dir and load all json dictionaries."""
        self.translations.clear()
        self.available_locales.clear()
        if not os.path.exists(self.locales_dir):
            os.makedirs(self.locales_dir, exist_ok=True)
            return

        json_files = sorted(glob.glob(os.path.join(self.locales_dir, "*.json")))
        for filepath in json_files:
            fname = os.path.basename(filepath)
            lang_code = os.path.splitext(fname)[0]
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.translations[lang_code] = data
                    meta = data.get("_meta", {})
                    self.available_locales.append({
                        "code": lang_code,
                        "name": meta.get("name", lang_code.upper()),
                        "flag": meta.get("flag", "🌐"),
                        "author": meta.get("author", "Community")
                    })
            except Exception as e:
                print(f"[i18n] Error loading {fname}: {e}")

        # Ensure 'en' is first in available_locales for consistent cycling
        self.available_locales.sort(key=lambda loc: (0 if loc["code"] == "en" else 1, loc["code"]))

    def detect_system_locale(self) -> str:
        """
        Detect system language from TrimUI Brick OS settings files or OS locale.
        Falls back strictly to 'en' (English) if none detected or unsupported.
        """
        # 1. Check TrimUI Brick hardware filesystem paths
        for path in TRIMUI_CANDIDATE_PATHS:
            if os.path.exists(path) and os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                    if not content:
                        continue
                    code = None
                    if content.startswith("{"):
                        data = json.loads(content)
                        for k in ("language", "lang", "locale", "code", "sys_lang"):
                            if k in data:
                                code = self._normalize_lang_code(data[k])
                                if code and code in self.translations:
                                    return code
                    else:
                        first_line = content.splitlines()[0]
                        code = self._normalize_lang_code(first_line)
                        if code and code in self.translations:
                            return code
                except Exception:
                    pass

        # 2. Check Linux environment variables
        for env_var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
            val = os.environ.get(env_var, "")
            if val:
                code = self._normalize_lang_code(val)
                if code and code in self.translations:
                    return code

        # 3. Default strictly to English
        return "en"

    def init_from_config(self):
        """Read preferred locale from settings.json or detect system locale."""
        settings_path = os.path.join(os.path.dirname(self.locales_dir), "settings.json")
        pref = "auto"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    pref = cfg.get("locale", "auto")
            except Exception:
                pass

        if pref == "auto" or pref not in self.translations:
            self.is_auto = True
            self.active_locale = self.detect_system_locale()
        else:
            self.is_auto = False
            self.active_locale = pref

    def set_locale(self, lang_code: str, save_to_settings: bool = True):
        """Switch active locale and optionally persist to settings.json."""
        if lang_code == "auto":
            self.is_auto = True
            self.active_locale = self.detect_system_locale()
        elif lang_code in self.translations:
            self.is_auto = False
            self.active_locale = lang_code
        else:
            print(f"[i18n] Unknown language code: {lang_code}")
            return

        if save_to_settings:
            settings_path = os.path.join(os.path.dirname(self.locales_dir), "settings.json")
            try:
                cfg = {}
                if os.path.exists(settings_path):
                    with open(settings_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                cfg["locale"] = "auto" if self.is_auto else self.active_locale
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"[i18n] Could not save language preference: {e}")

    def cycle_next_locale(self) -> str:
        """Cycle to next available language: auto -> en -> pl -> de -> es -> auto..."""
        codes = ["auto"] + [loc["code"] for loc in self.available_locales]
        current = "auto" if self.is_auto else self.active_locale
        try:
            cur_idx = codes.index(current)
            next_idx = (cur_idx + 1) % len(codes)
        except ValueError:
            next_idx = 0

        next_code = codes[next_idx]
        self.set_locale(next_code, save_to_settings=True)
        return self.get_current_display_name()

    def get_current_display_name(self) -> str:
        """Return formatted name e.g. '🇬🇧 English (en)' or '🌐 Auto [🇬🇧 EN]'."""
        if self.is_auto:
            flag = self.get_locale_flag(self.active_locale)
            return f"🌐 Auto [{flag} {self.active_locale.upper()}]"
        flag = self.get_locale_flag(self.active_locale)
        name = self.get_locale_name(self.active_locale)
        return f"{flag} {name} ({self.active_locale})"

    def get_locale_name(self, code: str) -> str:
        for loc in self.available_locales:
            if loc["code"] == code:
                return loc["name"]
        return code.upper()

    def get_locale_flag(self, code: str) -> str:
        for loc in self.available_locales:
            if loc["code"] == code:
                return loc["flag"]
        return "🌐"

    def t(self, key: str, default: Optional[Any] = None, **kwargs) -> Any:
        """
        Translate key using dot notation (e.g. 'common.back') or fallback.
        Supports lists (e.g. 'clock.days') and string interpolation {var}.
        """
        val = self._lookup(self.active_locale, key)
        if val is None and self.active_locale != self.fallback_locale:
            val = self._lookup(self.fallback_locale, key)
        if val is None:
            val = default if default is not None else key

        if kwargs and isinstance(val, str):
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return val

    def _lookup(self, lang_code: str, key: str) -> Optional[Any]:
        dict_data = self.translations.get(lang_code, {})
        parts = key.split(".")
        cur = dict_data
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return None
        return cur


# Global singleton instance
i18n = I18nManager()


def t(key: str, default: Optional[Any] = None, **kwargs) -> Any:
    """Convenience global translation function."""
    return i18n.t(key, default, **kwargs)
