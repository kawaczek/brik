# 🏗️ Architektura Systemu, Dynamiczny Loader i Silnik Wielojęzyczności (i18n)

Dokumentacja techniczna wewnętrznej architektury **BrickDeck OS**, dynamicznego systemu wtyczek oraz silnika internacjonalizacji.

---

## 🏛️ 1. Architektura Rdzenia (Core Framework)

BrickDeck został zaprojektowany z zachowaniem ścisłej separacji warstw:

```
+-------------------------------------------------------------------------+
|                              BrickDeckApp                               |
|        (Główna pętla zdarzeń, zarządzanie cyklem życia modułów)         |
+-------------------------------------------------------------------------+
       |                         |                          |
       v                         v                          v
+---------------+       +------------------+       +-------------------+
| InputManager  |       |      Canvas      |       |   DisplayDriver   |
| (evdev/term)  |       | (Pillow 2D/i18n) |       | (FB / Term / SDL) |
+---------------+       +------------------+       +-------------------+
                                 ^
                                 |
                        +------------------+
                        |   I18nManager    |
                        | (locales/*.json) |
                        +------------------+
                                 ^
                                 |
+-------------------------------------------------------------------------+
|                  BaseModule (modules/mod_*.py)                          |
|    (Każde narzędzie to niezależna klasa dziedzicząca po BaseModule)    |
+-------------------------------------------------------------------------+
```

### Podstawowe Komponenty:

1. **`core/module_base.py` (`BaseModule`):**
   * Klasa bazowa dla każdego narzędzia w systemie. Definiuje interfejs:
     * `on_load()`: Jednorazowa inicjalizacja po starcie.
     * `on_activate()` / `on_deactivate()`: Nawigacja na/z modułu.
     * `update(dt)`: Logika biznesowa, liczniki, odpytywanie wątków tła.
     * `render(canvas)`: Rysowanie widoku na buforze 1024×768.
     * `handle_input(event)`: Reakcja na przyciski gamepada.
     * `get_hotkey_hints()`: Dynamiczne etykiety dla dolnego paska nawigacji.

2. **`core/canvas.py` (`Canvas`):**
   * Silnik graficzny bazujący na bibliotece Pillow (PIL).
   * Generuje klatki w formacie BGRA (dokładnie 3 145 728 bajtów na klatkę: 1024 × 768 × 4).
   * Wbudowane komponenty cyberdecka:
     * Karuzela zakładek z dynamicznym oknem przesuwnym (`draw_header`).
     * Dolny pasek skrótów ze zlokalizowanymi pigułkami przycisków (`draw_footer`).
     * Ramki kart z podwójną obwódką (`draw_card`).
     * Wskaźniki paskowe (`draw_gauge`) i odznaki (`draw_badge`).
     * Analizator widma FFT (`draw_spectrum`), oscyloskop (`draw_oscilloscope`), miernik stereo (`draw_vu_meter`).

3. **`core/display_driver.py` (`DisplayDriver`):**
   * Uniwersalna warstwa wyjściowa:
     * `fb`: Bezpośredni zapis do bufora ramki Linuksa (`/dev/fb0`).
     * `term`: Rysowanie w terminalu za pomocą kodów 24-bit TrueColor ANSI.
     * `pygame`: Okno deweloperskie na komputerze PC.

4. **`core/input_manager.py` (`InputManager`):**
   * Zapewnia równoległą obsługę zdarzeń z linuksowego podsystemu `evdev` (przyciski konsoli TrimUI Brick) oraz emulacji klawiatury terminala na komputerze deweloperskim.

---

## 🔌 2. Dynamiczny Loader Wtyczek (`modules.json`)

Tradycyjne podejście z twardym importowaniem klas (`from modules.mod_xyz import ...`) w głównym pliku programu utrudniało rozbudowę systemu. W BrickDeck OS plik `brickdeck.py` **nie zawiera żadnego sztywnego importu modułów**.

### Jak działa dynamiczne ładowanie?
1. Podczas startu aplikacji wywoływana jest metoda `_load_modules()`.
2. Program odczytuje plik [modules.json](file:///home/kawak/brick/Apps/BrickDeck/modules.json):
   ```json
   {
       "auto_discover": true,
       "modules": [
           {"id": "mod_clock", "enabled": true, "name": "Zegar, Pogoda i Odjazdy MZK"},
           {"id": "mod_mzk_map", "enabled": true, "name": "Gorzow Live Fleet Radar"}
       ]
   }
   ```
3. Dla każdego modułu z flagą `"enabled": true`:
   * Używana jest funkcja `importlib.import_module(f"modules.{mod_id}")`.
   * Mechanizm refleksji (`inspect.isclass`) odnajduje klasę dziedziczącą po `BaseModule`.
   * Klasa jest instancjonowana i dodawana do listy aktywnych zakładek.
4. **Auto-Discovery:** Jeśli w folderze `modules/` pojawi się nowy plik (np. `mod_custom.py`), którego nie ma w `modules.json`, system automatycznie go załaduje i dopisze do pliku konfiguracyjnego bez konieczności restartu czy edycji kodu!

---

## 🌍 3. Silnik Wielojęzyczności (`core/i18n.py`)

Silnik internacjonalizacji pozwala na natywne korzystanie z BrickDeck OS użytkownikom z całego świata.

### Architektura Silnika:
* **Klasa `I18nManager`:**
  * Wczytuje słowniki JSON z katalogu `locales/`.
  * Śledzi aktywny język (`self.active_locale`) oraz język awaryjny (`self.fallback_locale = "en"`).
  * Zapewnia funkcję translacji `t(klucz, default, **kwargs)` z obsługą formatowania kropkowego (`common.back`) oraz zmiennych dynamicznych (`{lang}`).

### Schemat Łańcucha Fallback:
Gdy moduł zażąda tłumaczenia klucza:
```
1. Aktywny język (np. "de")
       | (jeśli brak klucza)
       v
2. Język międzynarodowy ("en")
       | (jeśli brak klucza)
       v
3. Język macierzysty ("pl")
       | (jeśli brak klucza)
       v
4. Wartość domyślna przekazana w kodzie (default)
```
Dzięki tej hierarchii system **nigdy nie wyświetli pustego pola ani nie zgłosi błędu braku klucza**.

---

## 📁 4. Struktura Plików Językowych (`locales/*.json`)

Każdy plik językowy to czysty dokument JSON posiadający metadane `_meta` oraz sekcje logiczne:

```json
{
    "_meta": {
        "code": "pl",
        "name": "Polski",
        "flag": "🇵🇱",
        "author": "BrickDeck Team"
    },
    "common": {
        "select": "Wybierz",
        "back": "Wróć",
        "modules": "Moduły",
        "navigation": "Ruch",
        "exit": "Wyjście"
    },
    "modules": {
        "mod_clock": "Zegar & MZK",
        "mod_camera": "CamScope"
    },
    "system": {
        "title": "TRIMUI BRICK HARDWARE TELEMETRY",
        "cpu_card": "PROCESOR (Allwinner A133P ARM64)",
        "lang_changed": "Zmieniono język na: {lang}"
    }
}
```

### Jak dodać nowy język (np. Francuski `fr.json`)?
1. Przejdź do katalogu `Apps/BrickDeck/locales/`.
2. Skopiuj plik `en.json` jako `fr.json`.
3. Zmień metadane na górze pliku:
   ```json
   "_meta": {
       "code": "fr",
       "name": "Français",
       "flag": "🇫🇷",
       "author": "Twoje Imię / Nick"
   }
   ```
4. Przetłumacz wartości tekstowe.
5. **Gotowe!** Po ponownym uruchomieniu BrickDeck natychmiast wykryje język francuski na liście dostępnych języków pod przyciskiem **Y**.
