# 📖 BrickDeck OS - Podręcznik Użytkownika i Instalacji

Kompletny przewodnik po instalacji, konfiguracji i obsłudze **BrickDeck OS** na przenośnej konsoli **TrimUI Brick** (oraz na komputerze PC w trybie deweloperskim).

---

## 📋 Spis Treści
1. [Specyfikacja Sprzętowa TrimUI Brick](#-specyfikacja-sprzętowa-trimui-brick)
2. [Instalacja na Karcie MicroSD](#-instalacja-na-karcie-microsd)
3. [Klawiszologia i Sterowanie](#-klawiszologia-i-sterowanie)
4. [Pliki Konfiguracyjne](#-pliki-konfiguracyjne)
   - [modules.json – Zarządzanie Modułami](#1-modulesjson--zarządzanie-modułami)
   - [settings.json – Ustawienia Systemowe i Język](#2-settingsjson--ustawienia-systemowe-i-język)
   - [transit_config.json – Pogoda, Komunikacja i Home Assistant](#3-transit_configjson--pogoda-komunikacja-i-home-assistant)
5. [Podłączanie Peryferiów USB-C OTG](#-podłączanie-peryferiów-usb-c-otg)
6. [Uruchamianie i Testowanie na PC](#-uruchamianie-i-testowanie-na-pc)
7. [Rozwiązywanie Problemów (FAQ)](#-rozwiązywanie-problemów-faq)

---

## 🕹️ Specyfikacja Sprzętowa TrimUI Brick

Konsola **TrimUI Brick** to miniaturowy, kieszonkowy komputer z systemem Linux, idealny jako baza dla taktycznego cyberdecka:

| Parametr | Wartość | Uwagi dla BrickDeck |
| :--- | :--- | :--- |
| **Procesor (SoC)** | Allwinner A133P (4x ARM Cortex-A53 @ 1.8 GHz) | Pełna obsługa 64-bitowego Pythona 3 |
| **Pamięć RAM** | 1024 MB LPDDR4 | Wszystkie 17 modułów zajmuje łącznie < 80 MB RAM |
| **Ekran** | 3.2" IPS, proporcje 4:3, **1024 × 768 pikseli** | Niezwykle wysoka ostrość (400 PPI), natywne renderowanie pixel-perfect |
| **Kontrolery** | D-Pad (Krzyżak), A, B, X, Y, Bumpery L1 / R1, L2 / R2, Menu / Start | 100% nawigacji bez konieczności dotyku czy myszy |
| **Łączność** | Wi-Fi 802.11 b/g/n, Bluetooth 4.2 BLE | Skanery sieci, radar BLE, API OpenSky / RainViewer / MZK |
| **Porty** | USB Type-C OTG (Host / Gadget), Slot MicroSD, Audio Jack 3.5mm | Kamery inspekcyjne, konwertery UART, SDR, Flipper Zero |
| **Bateria** | 3000 mAh Li-Po (~4-5 godzin ciągłej pracy) | Telemetria napięcia w czasie rzeczywistym |

---

## 💾 Instalacja na Karcie MicroSD

### Krok 1: Przygotowanie plików
Upewnij się, że na karcie microSD znajduje się standardowy system TrimUI (np. fabryczny OS lub MinUI / CrossMix).

### Krok 2: Kopiowanie katalogu BrickDeck
Skopiuj cały folder `Apps/BrickDeck` do katalogu `Apps` na karcie SD:
```bash
cp -r /home/kawak/brick/Apps/BrickDeck /media/$USER/SDCARD/Apps/
```

### Krok 3: Struktura katalogów na karcie SD
Docelowa struktura powinna wyglądać następująco:
```
SDCARD/
├── Apps/
│   └── BrickDeck/
│       ├── brickdeck.py          # Główny koordynator systemu
│       ├── launch.sh             # Skrypt startowy dla menu TrimUI
│       ├── config.json / icon.png
│       ├── modules.json          # Konfiguracja włączonych wtyczek
│       ├── settings.json         # Konfiguracja języka i motywu
│       ├── transit_config.json   # Konfiguracja GPS i przystanków
│       ├── core/                 # Silnik graficzny, i18n, input, canvas
│       ├── locales/              # Paczki językowe (pl, en, de, es)
│       ├── modules/              # Pliki wtyczek mod_*.py
│       └── captures/             # Zdjęcia z kamery inspekcyjnej (CamScope)
```

### Krok 4: Uruchomienie na konsoli
1. Włóż kartę do konsoli TrimUI Brick i włącz zasilanie.
2. W głównym menu wejdź do zakładki **Apps**.
3. Wybierz ikonę **BrickDeck** – system uruchomi się w natywnej rozdzielczości 1024×768!

---

## 🎮 Klawiszologia i Sterowanie

Framework został zoptymalizowany pod kątem wygody trzymania konsoli w dłoniach:

| Przycisk TrimUI Brick | Klawisz PC (Test) | Globalna Akcja | Działanie w aktywnym module |
| :--- | :--- | :--- | :--- |
| **Bumper L1** | **Q** | Przełącz na **poprzedni moduł** (w lewo) | – |
| **Bumper R1** | **E** | Przełącz na **następny moduł** (w prawo) | – |
| **D-Pad Góra / Dół** | **W / S** lub Strzałki | – | Przewijanie list, regulacja ekspozycji, wybór |
| **D-Pad Lewo / Prawo** | **A / D** lub Strzałki | – | Zmiana zoomu, zmiana klatki radaru, zmiana kanału |
| **Przycisk A** | **Spacja / Enter** | – | **Główna akcja:** Zrób zdjęcie / Wymuś odświeżenie / Wybierz |
| **Przycisk B** | **B / Backspace** | – | **Powrót:** Zamknij modal / Wróć / Anuluj |
| **Przycisk X** | **X** | – | **Akcja dodatkowa:** Zmiana filtra wizyjnego / Zmiana przystanku / Zmiana motywu |
| **Przycisk Y** | **Y** | – | **Opcje modułu:** Przełącznik języka (w Systemie) / Siatka celownicza / Styl animacji |
| **Przycisk Menu / Start**| **M / Esc** | **Bezpieczne wyjście** do menu TrimUI | Zatrzymanie wątków i zwolnienie bufora ekranu |

---

## ⚙️ Pliki Konfiguracyjne

### 1. `modules.json` – Zarządzanie Modułami
Plik [modules.json](file:///home/kawak/brick/Apps/BrickDeck/modules.json) pozwala na włączanie, wyłączanie oraz zmianę kolejności modułów na górnym pasku zakładek:

```json
{
    "description": "Lista aktywnych modulow BrickDeck OS.",
    "auto_discover": true,
    "modules": [
        {"id": "mod_clock", "enabled": true, "name": "Zegar, Pogoda i Odjazdy MZK"},
        {"id": "mod_air_radar", "enabled": true, "name": "Global Aerospace & Satellites"},
        {"id": "mod_camera", "enabled": true, "name": "CamScope Borescope & Camera"},
        {"id": "mod_flipper", "enabled": false, "name": "Flipper Zero (Wylaczony)"}
    ]
}
```
* **`enabled` (true/false):** Moduły wyłączone nie zużywają pamięci RAM ani procesora i nie pojawiają się w menu.
* **`auto_discover` (true):** Wrzucenie nowego pliku `mod_*.py` do katalogu `modules/` spowoduje jego automatyczną rejestrację.

---

### 2. `settings.json` – Ustawienia Systemowe i Język
Plik [settings.json](file:///home/kawak/brick/Apps/BrickDeck/settings.json) przechowuje globalne preferencje:

```json
{
    "locale": "auto",
    "theme": "cyber_dark"
}
```
* **`locale`:** Dostępne wartości: `"auto"` (wykrywanie z systemu), `"pl"`, `"en"`, `"de"`, `"es"`.
* Język można w każdej chwili zmienić w locie klawiszem **Y** w module *System Telemetry*.

---

### 3. `transit_config.json` – Pogoda, Komunikacja i Home Assistant
Plik [transit_config.json](file:///home/kawak/brick/Apps/BrickDeck/transit_config.json) definiuje parametry geolokalizacyjne i integracje:

```json
{
    "city": "Gorzow Wielkopolski",
    "coordinates": {
        "lat": 52.7333,
        "lon": 15.2333
    },
    "active_stop_idx": 0,
    "animation_style": "starfield",
    "screensaver_timeout_sec": 60,
    "hass_url": "http://homeassistant.local:8123",
    "hass_token": "TWÓJ_TOKEN_BEARER",
    "stops": [
        {"name": "Katedra", "id": "000000000095", "code": "8"},
        {"name": "AWF", "id": "000000000005", "code": "12"}
    ]
}
```

---

## 🔌 Podłączanie Peryferiów USB-C OTG

Konsola TrimUI Brick posiada port USB-C z obsługą trybu **OTG Host**. Wystarczy użyć adaptera USB-C na USB-A, aby podłączyć:

1. **Kamery Inspekcyjne / Endoskopy Borescope:**
   * Wykrywane automatycznie jako `/dev/video0` lub `/dev/video1`.
   * Moduł `CamScope` automatycznie przełącza się z symulatora na żywy obraz wideo z kamery.
2. **Flipper Zero:**
   * Podłączenie przez kabel USB-C pozwala na mirror ekranu w skali 8x oraz sterowanie pilotem za pomocą przycisków konsoli.
3. **Konwertery USB-UART (CH340, CP2102, FT232R):**
   * Wykrywane jako `/dev/ttyUSB0` lub `/dev/ttyACM0`.
   * Moduł `mod_uart.py` pozwala na bezpośredni podgląd logów startowych routerów, ESP32 czy Arduino.
4. **Tethering Bluetooth (Pwngotchi):**
   * Po sparowaniu przez Bluetooth PAN (`bnep0`), BrickDeck łączy się z adresem `192.168.44.44:8080`, pobierając stan zwierzaka.

---

## 💻 Uruchamianie i Testowanie na PC

Do testów deweloperskich nie potrzebujesz fizycznej konsoli! BrickDeck posiada wbudowany sterownik terminalowy ANSI 24-bit oraz opcjonalny sterownik Pygame.

### Uruchomienie w terminalu:
```bash
python3 /home/kawak/brick/Apps/BrickDeck/brickdeck.py --mode term
```
* Interfejs renderuje się bezpośrednio w Twoim oknie terminala w pełnym kolorze.
* Używaj klawiszy **Q / E** do przełączania modułów oraz **W / S / A / D / Spacja** do nawigacji.

---

## ❓ Rozwiązywanie Problemów (FAQ)

**P: Dlaczego moduł samolotów i ISS działa, mimo że nie mam podłączonego odbiornika SDR?**  
*O: Wszystkie moduły w BrickDeck posiadają tryb zerowych wymagań sprzętowych (Zero Hardware Requirement). Gdy nie ma podłączonego fizycznego tunera USB, system automatycznie pobiera pozycje samolotów na żywo z OpenSky Network, a pozycję ISS z serwerów telemetrycznych NASA.*

**P: Po minucie bezczynności włącza się zegar. Czy można to wyłączyć?**  
*O: Tak! W pliku `transit_config.json` zmień wartość `"screensaver_timeout_sec": 0`, aby całkowicie wyłączyć automatyczny wygaszacz.*

**P: Gdzie zapisują się zdjęcia zrobione kamerą inspekcyjną?**  
*O: Klatki są zapisywane w formacie PNG w folderze `SDCARD/Photos/` (jeśli istnieje) lub lokalnie w `Apps/BrickDeck/captures/`.*
