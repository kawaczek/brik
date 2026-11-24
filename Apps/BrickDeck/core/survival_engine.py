"""
BrickDeck Survival Engine (core/survival_engine.py)
Extensible data loader, parser, and indexer for survival field manuals and guides.
Supports both structured JSON files and human-readable Markdown (.md) documents.
Enables instant hot-reloading and automatic discovery of user-created guides.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("SurvivalEngine")


class SurvivalEngine:
    """Manages categories, loaded guides, search indexing, and parsing."""

    def __init__(self, base_data_dir: Optional[str] = None):
        if base_data_dir is None:
            # Default to Apps/BrickDeck/data/survival
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.normpath(os.path.join(current_dir, "..", "data", "survival"))
        else:
            self.base_dir = base_data_dir

        self.categories_file = os.path.join(self.base_dir, "categories.json")
        self.guides_dir = os.path.join(self.base_dir, "guides")
        self.custom_dir = os.path.join(self.base_dir, "custom")

        self.categories: List[Dict[str, Any]] = []
        self.categories_map: Dict[str, Dict[str, Any]] = {}
        self.guides_by_category: Dict[str, List[Dict[str, Any]]] = {}
        self.all_guides: List[Dict[str, Any]] = []

        self.load_all()

    def load_all(self):
        """Reload all categories, guides, and custom documents from disk."""
        self._load_categories()
        self._scan_and_load_guides()

    def _load_categories(self):
        self.categories = []
        self.categories_map = {}
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.categories = data.get("categories", [])
                    for cat in self.categories:
                        self.categories_map[cat["id"]] = cat
            except Exception as e:
                logger.error(f"Error loading categories: {e}")

        if not self.categories:
            # Fallback default categories
            self.categories = [
                {"id": "water", "name": "Woda & Filtracja", "icon": "💧", "badge": "PRIORYTET #1", "color": [0, 210, 255]},
                {"id": "power", "name": "Energia & Zasilanie", "icon": "⚡", "badge": "ENERGIA OFF-GRID", "color": [255, 170, 0]},
                {"id": "shelter", "name": "Schronienie & Zima", "icon": "🏕️", "badge": "TERMIKA", "color": [0, 230, 118]},
                {"id": "fire", "name": "Ogień & Ciepło", "icon": "🔥", "badge": "BEZ ZAPAŁEK", "color": [255, 82, 82]},
                {"id": "nav", "name": "Nawigacja & Orientacja", "icon": "🧭", "badge": "BEZ GPS", "color": [255, 215, 0]},
                {"id": "radio", "name": "Łączność & SOS", "icon": "🆘", "badge": "ŁĄCZNOŚĆ AWARYJNA", "color": [255, 61, 0]},
                {"id": "firstaid", "name": "Pierwsza Pomoc", "icon": "🩹", "badge": "RATOWNICTWO", "color": [233, 30, 99]},
                {"id": "knots", "name": "Węzły & Pionierka", "icon": "🪢", "badge": "LINY & WEZŁY", "color": [178, 255, 89]},
                {"id": "food", "name": "Żywność & Dzika Kuchnia", "icon": "🍃", "badge": "TEST JADALNOŚCI", "color": [102, 187, 106]},
                {"id": "tools", "name": "Kalkulatory & Narzędzia", "icon": "🧮", "badge": "INTERAKTYWNE", "color": [187, 134, 252]}
            ]
            for cat in self.categories:
                self.categories_map[cat["id"]] = cat

        self.guides_by_category = {cat["id"]: [] for cat in self.categories}
        self.all_guides = []

    def _scan_and_load_guides(self):
        """Scans both guides_dir and custom_dir for .json and .md files."""
        dirs_to_scan = [self.guides_dir, self.custom_dir]
        for d in dirs_to_scan:
            if not os.path.exists(d):
                try:
                    os.makedirs(d, exist_ok=True)
                except Exception:
                    continue

            for fname in sorted(os.listdir(d)):
                fpath = os.path.join(d, fname)
                if not os.path.isfile(fpath):
                    continue

                if fname.endswith(".json"):
                    guide = self._parse_json_guide(fpath)
                    if guide:
                        self._register_guide(guide)
                elif fname.endswith(".md"):
                    guide = self._parse_markdown_guide(fpath)
                    if guide:
                        self._register_guide(guide)

    def _register_guide(self, guide: Dict[str, Any]):
        cat_id = guide.get("category", "other")
        if cat_id not in self.guides_by_category:
            self.guides_by_category[cat_id] = []
        self.guides_by_category[cat_id].append(guide)
        self.all_guides.append(guide)

    def _parse_json_guide(self, fpath: str) -> Optional[Dict[str, Any]]:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "id" not in data:
                data["id"] = os.path.splitext(os.path.basename(fpath))[0]
            if "title" not in data:
                data["title"] = data["id"].replace("_", " ").title()
            if "badge" not in data:
                data["badge"] = "PORADNIK"
            if "category" not in data:
                data["category"] = "water"

            # Parse lines/sections into standard display tuples (text, style_type)
            # style_type: "header", "subheader", "text", "step", "warn", "ok", "tip", "empty"
            parsed_lines = []
            if "lines" in data and isinstance(data["lines"], list):
                for item in data["lines"]:
                    if isinstance(item, list) and len(item) >= 2:
                        parsed_lines.append((str(item[0]), str(item[1])))
                    elif isinstance(item, str):
                        parsed_lines.append((item, "text"))
            elif "sections" in data and isinstance(data["sections"], list):
                for sec in data["sections"]:
                    heading = sec.get("heading")
                    sec_type = sec.get("type", "subheader")
                    if heading:
                        parsed_lines.append((heading, "header"))
                    for line in sec.get("lines", []):
                        parsed_lines.append((line, sec_type))
                    parsed_lines.append(("", "empty"))

            data["parsed_lines"] = parsed_lines
            data["file_path"] = fpath
            data["is_custom"] = ("custom" in fpath)
            return data
        except Exception as e:
            logger.error(f"Error parsing JSON guide {fpath}: {e}")
            return None

    def _parse_markdown_guide(self, fpath: str) -> Optional[Dict[str, Any]]:
        """Parses a Markdown survival guide with metadata block and markdown formatting."""
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            base_id = os.path.splitext(os.path.basename(fpath))[0]
            title = base_id.replace("_", " ").title()
            category = "water"
            badge = "PRZEWODNIK MD"
            priority = "NORMAL"
            tags = []

            lines = raw_text.splitlines()
            parsed_lines: List[Tuple[str, str]] = []

            for line in lines:
                sline = line.strip()
                if not sline:
                    parsed_lines.append(("", "empty"))
                    continue

                # Main Title # ...
                if sline.startswith("# ") and title == base_id.replace("_", " ").title():
                    title = sline[2:].strip()
                    continue

                # Metadata tag line e.g. > Kategoria: water | Priorytet: HIGH | Badge: FILTRACJA
                if sline.startswith(">") and ("kategoria:" in sline.lower() or "category:" in sline.lower()):
                    parts = [p.strip() for p in sline.lstrip(">").split("|")]
                    for part in parts:
                        if ":" in part:
                            k, v = [x.strip() for x in part.split(":", 1)]
                            kl = k.lower()
                            if kl in ("kategoria", "category"):
                                category = v.lower()
                            elif kl in ("badge", "odznaka"):
                                badge = v.upper()
                            elif kl in ("priorytet", "priority"):
                                priority = v.upper()
                            elif kl in ("tags", "tagi"):
                                tags = [t.strip() for t in v.split(",")]
                    continue

                # Callout blocks e.g. > [!WARNING], > [!IMPORTANT], > [!TIP]
                if sline.startswith("> [!WARNING]") or sline.startswith("> [!CAUTION]"):
                    parsed_lines.append(("⚠️ OSTRZEŻENIE:", "warn"))
                    continue
                elif sline.startswith("> [!IMPORTANT]") or sline.startswith("> [!ALERT]"):
                    parsed_lines.append(("🚨 WAŻNE:", "warn"))
                    continue
                elif sline.startswith("> [!TIP]") or sline.startswith("> [!NOTE]"):
                    parsed_lines.append(("💡 WSKAZÓWKA:", "tip"))
                    continue
                elif sline.startswith(">"):
                    # Quote or callout content
                    quote_text = sline.lstrip(">").strip()
                    parsed_lines.append((quote_text, "tip"))
                    continue

                # Markdown H2 ## ...
                if sline.startswith("## "):
                    parsed_lines.append(("", "empty"))
                    parsed_lines.append((sline[3:].strip(), "header"))
                    continue

                # Markdown H3 ### ...
                if sline.startswith("### "):
                    parsed_lines.append((sline[4:].strip(), "subheader"))
                    continue

                # Steps / Numbered list 1. ...
                if re.match(r"^\d+\.\s+", sline):
                    parsed_lines.append((sline, "step"))
                    continue

                # Bullet points •, -, *
                if sline.startswith(("- ", "* ", "• ")):
                    parsed_lines.append((sline, "bullet"))
                    continue

                # Normal paragraph text
                parsed_lines.append((sline, "text"))

            guide = {
                "id": base_id,
                "title": title,
                "category": category,
                "badge": badge,
                "priority": priority,
                "tags": tags,
                "parsed_lines": parsed_lines,
                "file_path": fpath,
                "is_custom": ("custom" in fpath)
            }
            return guide
        except Exception as e:
            logger.error(f"Error parsing Markdown guide {fpath}: {e}")
            return None

    def get_categories(self) -> List[Dict[str, Any]]:
        return self.categories

    def get_guides_for_category(self, cat_id: str) -> List[Dict[str, Any]]:
        return self.guides_by_category.get(cat_id, [])

    def search_guides(self, query: str) -> List[Dict[str, Any]]:
        """Searches titles, tags, and content lines for a given keyword."""
        q = query.lower().strip()
        if not q:
            return self.all_guides

        results = []
        for g in self.all_guides:
            # Check title
            if q in g.get("title", "").lower():
                results.append(g)
                continue
            # Check tags
            tags = [t.lower() for t in g.get("tags", [])]
            if any(q in t for t in tags):
                results.append(g)
                continue
            # Check badge
            if q in g.get("badge", "").lower():
                results.append(g)
                continue
            # Check lines
            matched = False
            for line_text, _ in g.get("parsed_lines", []):
                if q in line_text.lower():
                    results.append(g)
                    matched = True
                    break
        return results
