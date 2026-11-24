# ⚡ TrimUI Brick Hacker Suite & BrickDeck OS

Kompleksowy zestaw oprogramowania i modularny framework GUI dla przenośnej konsoli **TrimUI Brick** (ekran 1024×768 IPS, Allwinner A133P Linux).

---

## 🌟 FLAGOWY PROJEKT: [BrickDeck OS](file:///home/kawak/brick/Apps/BrickDeck) (Modularny Framework GUI)

Zamiast uruchamiać każdy program osobno, **BrickDeck** łączy wszystkie narzędzia w **jeden spójny, profesjonalny system operacyjny** z cyberpunkowym interfejsem w rozdzielczości 1024×768:

```
+---------------------------------------------------------------------------------+
| ⚡ BRICKDECK   [L1]  [🐬 Flipper]  [👻 Pwngotchi]  [📡 BLE Radar]  [R1]   🔋 88% 18:45 |
+---------------------------------------------------------------------------------+
|                                                                                 |
|                        AKTYWNY MODUŁ ROBOCZY (1024 x 672)                       |
|                                                                                 |
|  * Desk Clock & MZK: zegar biurkowy, pogoda, tablica odjazdów MZK Gorzów i animacje |
|  * MZK Gorzów Mapa: radar floty na żywo (GPS), wektorowa mapa z Wartą i tramwajami  |
|  * Radar Opadów & Burz: mapa radarowa IMGW / RainViewer z animacją klatek chmur     |
|  * Global Aerospace Radar: obracający się globus 3D, orbity ISS/satelitów + ADS-B   |
|  * Global Lightning Radar: uderzenia piorunów Blitzortung na żywo i licznik grzmotu |
|  * Universal Planetarium: model 3D fazy Księżyca, kopuła nieba i przeloty stacji ISS|
|  * NOAA Space Weather: wiatr słoneczny DSCOVR, rozbłyski GOES X-Ray i owal zorzy    |
|  * Tactical Enigma Lab: wojskowa Enigma M3, generator OTP z /dev/urandom i Randomart|
|  * Global Seismology: sejsmograf bębnowy na żywo, trzęsienia ziemi USGS i tsunami   |
|  * Flipper Zero: ekran 128x64 w skali 6x/8x + bezpośrednie sterowanie D-Pad          |
|  * Pwngotchi: animowany zwierzak na żywo + motywy (Cyberpunk, Matrix, Amber)         |
|  * Cyber Radio: streaming SomaFM/Kohina/Trójka + 32-pasmowy wizualizator spektrum   |
|  * NetScan Recon: skaner Wi-Fi LAN z bazą OUI producentów i audytem otwartych portów|
|  * BLE Radar: taktyczny okrągły radar 360° z wykrywaniem urządzeń Bluetooth           |
|  * Wi-Fi Spectrum: analizator zajętości 14 kanałów 2.4 GHz + lista sieci              |
|  * Hardware Pinouts: podręczna ściągawka GPIO (RPi 40-Pin, ESP32, Flipper, USB-C)    |
|  * Calc & Net Utils: kalkulator podsieci CIDR / IPv4, konwerter Radix i rezystory    |
|  * Home Assistant: kieszonkowy pilot inteligentnego domu z kafelkami urządzeń 2x4    |
|  * UART Terminal: kieszonkowy monitor portu szeregowego USB-C (ESP32/Arduino)         |
|  * CamScope Borescope: kamera inspekcyjna USB/Wi-Fi z 5 filtrami wizyjnymi i zoomem  |
|  * Hardware Diag Lab: tester gamepada, martwych pikseli matrycy i głośników stereo   |
|  * System Telemetry: obciążenie 4 rdzeni CPU Cortex-A53, RAM, temperatura i zasilanie|
|                                                                                 |
+---------------------------------------------------------------------------------+
| [L1/R1]: Zmień moduł | [D-Pad]: Nawigacja | [A]: Wybierz | [B]: Wróć | [Menu]: Exit|
+---------------------------------------------------------------------------------+
```

### Sterowanie w BrickDeck:
* **Bumpery L1 / R1** (lub klawisze **Q / E** na PC) – błyskawiczne przełączanie zakładek na górnym pasku!
* **Krzyżak (D-Pad)** – sterowanie wewnątrz aktywnego modułu.
* **Przycisk A** – potwierdzenie / akcja.
* **Przycisk B** – powrót / anuluj.
* **Przycisk X** – akcja specjalna (np. zmiana motywu kolorów, reskanowanie).

---

## 📂 Struktura katalogów w repozytorium

```
/home/kawak/brick/
├── Apps/
│   ├── BrickDeck/             # 🌟 FLAGOWY MODULARNY FRAMEWORK GUI
│   │   ├── brickdeck.py       # Główny silnik aplikacji i pętla zdarzeń
│   │   ├── config.json        # Wpis do menu TrimUI
│   │   ├── icon.png           # Cyberdeck ikona 256x256
│   │   ├── launch.sh          # Launcher konsolowy
│   │   ├── transit_config.json# Konfiguracja przystanków Gorzowa i wygaszacza
│   │   ├── core/              # Silnik: canvas, input_manager, display_driver, theme
│   │   ├── modules/           # Wtyczki: clock/mzk, flipper, pwngotchi, radar, wifi, uart, system
│   │   └── README.md          # Jak pisać własne moduły w 5 minut
│   ├── BrickFlipper/          # Samodzielna wersja dedykowana dla Flipper Zero
│   └── Brickgotchi/           # Samodzielna wersja dedykowana dla Pwngotchi
├── docs/
│   └── GORZOW_MZK_API.md      # 🚍 KOMPLETNA DOKUMENTACJA API MZK GORZÓW (21 endpointów)
├── tools/
│   ├── gorzow_mzk.py          # 🚍 Narzędzie CLI do badania floty GPS, odjazdów i smogu
│   ├── simulate_flipper.py    # Symulator sprzętowy Flippera Zero (PTY)
│   └── simulate_pwngotchi.py  # Symulator serwera HTTP Pwngotchi
└── README.md
```

---

## 🧪 Przetestuj BrickDeck już TERAZ na PC!

Wystarczy jedno polecenie w terminalu:
```bash
python3 /home/kawak/brick/Apps/BrickDeck/brickdeck.py --mode term
```
*Zobaczysz pełny, interaktywny dashboard w 24-bitowych kolorach ANSI. Używaj klawiszy **Q / E**, aby spacerować po wszystkich 6 modułach!*

---

## 🚀 Wgrywanie jutro na kartę microSD

Po rozpakowaniu konsolki TrimUI Brick:
1. Włóż kartę microSD do komputera.
2. Skopiuj cały folder `Apps`:
   ```bash
   cp -r /home/kawak/brick/Apps/* /sciezka/do/karty_sd/Apps/
   ```
3. Włóż kartę do konsoli i ciesz się potężnym kieszonkowym cyberdeckiem!
