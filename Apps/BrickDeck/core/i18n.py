"""
BrickDeck i18n (Internationalization) Engine
Supports multi-language UI, fallback to English/Polish, system locale auto-detection,
and JSON locale packs in Apps/BrickDeck/locales/*.json.
"""

import os
import json
import glob
from typing import Dict, Any, Optional, List


class I18nManager:
    """Manages translations and locale switching for BrickDeck OS."""

    def __init__(self, locales_dir: Optional[str] = None):
        if locales_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            locales_dir = os.path.join(base_dir, "locales")
        self.locales_dir = locales_dir
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.active_locale = "pl"
        self.fallback_locale = "en"
        self.is_auto = True
        self.available_locales: List[Dict[str, str]] = []

        self.load_all_locales()
        self.init_from_config()

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
                print(f"[i18n] Blad ladowania {fname}: {e}")

    def detect_system_locale(self) -> str:
        """Detect language from environment variables or OS locale."""
        for env_var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
            val = os.environ.get(env_var, "")
            if val:
                code = val.split(".")[0].split("_")[0].lower()
                if code in self.translations:
                    return code
        return "pl" if "pl" in self.translations else ("en" if "en" in self.translations else "pl")

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
            print(f"[i18n] Nieznany kod jezyka: {lang_code}")
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
                print(f"[i18n] Nie udalo sie zapisac ustawien jezyka: {e}")

    def cycle_next_locale(self) -> str:
        """Cycle to next available language: auto -> pl -> en -> de -> es -> auto..."""
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
        """Return formatted name e.g. '🇵🇱 Polski (pl)' or '🌐 Auto [pl]'."""
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
        if val is None and self.fallback_locale != "pl":
            val = self._lookup("pl", key)
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
