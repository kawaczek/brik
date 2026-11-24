# ⚡ BrickDeck OS - Modułowy Framework GUI dla TrimUI Brick

**BrickDeck** to lekki, modularny framework GUI w stylu **Tactical Cyberdeck / Sci-Fi Dark Mode**, zaprojektowany od podstaw dla przenośnej konsoli **TrimUI Brick** (ekran 1024×768 IPS, Allwinner A133P Linux).

Łączy wszystkie narzędzia diagnostyczne, piloty i sensory w **jeden spójny, profesjonalny system operacyjny** obsługiwany w 100% z poziomu gamepadu (D-Pad, ABXY, L1/R1).

---

## 🎮 Klawiszologia i Sterowanie w BrickDeck

| Przycisk na konsoli | Klawisz na PC (Test) | Działanie w systemie |
| :--- | :--- | :--- |
| **Bumper L1** | **Q** | Poprzednia zakładka / moduł |
| **Bumper R1** | **E** | Następna zakładka / moduł |
| **D-Pad (Góra/Dół/Lewo/Prawo)** | **W / S / A / D** lub Strzałki | Nawigacja po menu, listach i opcjach modułu |
| **Przycisk A** | **Spacja / Enter** | Wybierz / Akcja / Potwierdź |
| **Przycisk B** | **B / Backspace / Esc** | Wróć / Anuluj |
| **Przycisk X** | **X** | Dodatkowa akcja modułu (np. zmiana motywu, reskan) |
| **Przycisk Y** | **Y** | Opcje modułu (np. zmiana IP, tryb) |
| **Przycisk Menu / Start** | **M / Esc** | Bezpieczne wyjście z aplikacji do menu konsoli |

---

## 🧩 Wbudowane Moduły (27 Narzędzi)

1. **🕒 Desk Clock, Screensaver, Pogoda & Odjazdy MZK (`mod_clock.py`):**
   * **Wielki zegar cyfrowy (54pt)** z pełną polską datą (`Poniedziałek, 23 Listopada 2026`).
   * **Prognoza pogody na żywo (Open-Meteo):** temperatura w °C, ikona pogody (☀️/⛅/🌧️/❄️), wiatr i zachmurzenie (bez żadnych kluczy API!).
   * **Wirtualna Tablica Odjazdów MZK Gorzów (SIP):** odjazdy w czasie rzeczywistym, licznik minut, badge `>>> ZA CHWILĘ <<<`.
   * **Płynne animacje w tle (przełączane klawiszem Y):** *3D Starfield*, *Matrix Rain*, *Retro Synthwave*.
   * **Automatyczny wygaszacz:** po 60 sekundach bezczynności konsola sama przechodzi w ten tryb.

2. **🗺️ Gorzów Live Transit Map & Fleet Radar (`mod_mzk_map.py`):**
   * **Wektorowa mapa Gorzowa:** zakola rzeki Warty, osie komunikacyjne, pętle Silwana, Wieprzyce, Piaski, Górczyn, Katedra.
   * **Flota MZK na żywo (GPS):** pobieranie pozycji tramwajów (linie 1, 2, 3 w bursztynie) i autobusów (linie 101, 104, 124... w cyjanie).
   * **Strzałki zwrotu (Bearing):** kierunki jazdy wozów, centrowanie mapy klawiszem **A**, zoom **X / Y**, filtr **B**.

3. **🌧️ Storm & Precipitation Radar (`mod_rain.py`):**
   * **Radar burz i opadów IMGW / RainViewer:** zasięg Zachodniej Polski i Ziemi Lubuskiej (Gorzów, Szczecin, Poznań, Zielona Góra, Berlin).
   * **Animowana oś czasu chmur deszczowych:** 8 klatek od -60 min do +45 min z przemieszczaniem frontów.
   * **Skala odbiciowości radarowej dBZ:** od mżawki (15 dBZ) po gwałtowne burze z gradem (65 dBZ). Klawisze **Lewo/Prawo** przewijają klatki, **A** pauzuje animację.

4. **🛰️ Global Aerospace & Satellite Radar (`mod_air_radar.py`):**
   * **Taktyczny Globus 3D i Orbity Satelitów:** obracająca się kula ziemska z zarysami kontynentów, południkami i orbitami wokółziemskimi.
   * **Satelity na żywo:** pozycja Międzynarodowej Stacji Kosmicznej (**ISS**) na żywo z API `wheretheiss.at` (złoty model z panelami słonecznymi, prędkość 27 600 km/h, pułap 416 km), chińska stacja Tiangong, NOAA-19 oraz konstelacje Starlink.
   * **Kinowy Multi-Level Zoom (Klawisze X / Y):** od pełnego widoku z kosmosu (1.0x) po taktyczny radar naziemny ADS-B z samolotami wokół wybranego celu (35.0x)!
   * **Globalny Wybór Lokalizacji (Klawisz B):** wyszukiwarka miast świata przez Nominatim lub wprowadzanie koordynatów GPS.

5. **🚢 Global Marine Traffic & AIS Radar (`mod_marine.py`):**
   * **Nawigacyjny radar morski PPI 360°:** obracająca się wiązka radaru z poświatą luminoforu, pierścienie zasięgu (2 NM, 5 NM, 10 NM, 25 NM, 50 NM), wektorowe kontury linii brzegowej.
   * **Śledzenie statków AIS w czasie rzeczywistym:** kontenerowce, tankowce, promy pasażerskie, holowniki i kutry rybackie z wektorami kursu (COG) i prędkości (SOG).
   * **Baza kluczowych szlaków i portów morskich:** Zatoka Pomorska / Świnoujście, Zatoka Gdańska, Kanał La Manche / Cieśnina Dover, Cieśnina Gibraltarska, Port Rotterdam, Cieśnina Bosfor, Cieśnina Malakka / Singapur.
   * **Pełna telemetria jednostki:** numer MMSI, znak wywoławczy Callsign, bandera, wymiary (dł x szer), zanurzenie (draught w metrach), port docelowy i ETA.

6. **⚡ Global Lightning Radar Blitzortung (`mod_blitz.py`):**
   * **Uderzenia piorunów na żywo na świecie:** wyładowania atmosferyczne w czasie rzeczywistym z sieci Blitzortung (Europa, USA, Azja, cały glob).
   * **Wiek uderzeń:** kodowanie kolorami (biały < 1 min, żółty < 5 min, pomarańczowy < 10 min, czerwony > 10 min) z pulsującymi falami uderzeniowymi.
   * **Kalkulator fali dźwiękowej grzmotu:** dokładna odległość do najbliższego pioruna w km i odliczanie sekund do nadejścia fali grzmotu!

7. **🌌 Universal Planetarium & ISS Passes (`mod_sky.py`):
   * **Model 3D fazy Księżyca:** fotorealistyczna, cieniowana kula księżycowa z kraterami, terminatorem i wyliczaniem dni do najbliższej Pełni.
   * **Interaktywna kopuła nieba 360°:** gwiazdozbiory (Wielki Wóz, Orion, Trójkąt Letni) i najjaśniejsze gwiazdy (Syriusz, Wega, Polaris, Betelgeza) w 100% offline.
   * **Rozpiska przelotów ISS:** najbliższe przeloty stacji kosmicznej widoczne gołym okiem z pułapem, czasem trwania i azymutem dla wybranego miasta na Ziemi.

8. **☀️ NOAA Space Weather & Aurora Oval (`mod_space.py`):
   * **Pogoda kosmiczna NASA / NOAA:** wiatr słoneczny w czasie rzeczywistym (sonda DSCOVR w punkcie L1: prędkość km/s, gęstość i pole Bz).
   * **Tarcza Słońca NASA SDO:** model ultrafioletowy 193Å z naniesionymi grupami plam słonecznych.
   * **Owal zorzy polarnej (Aurora Borealis / Australis):** biegunowa projekcja zasięgu zorzy polarnej z indeksem planetarnym Kp (0–9) i alertem widoczności w Polsce!

9. **🕵️ Tactical Cipher & Enigma Lab (`mod_crypto.py`):
   * **Symulator maszyny Enigma M3:** wierne okablowanie rotorów I–III, reflektor B i łącznica kablowa Steckerbrett z animowaną tablicą żarówek (Glühlampen) i taśmą dalekopisu.
   * **Generator One-Time Pad (OTP):** generowanie absolutnie niełamalnych 5-znakowych wojskowych grup szyfrujących z entropii procesora `/dev/urandom`.
   * **Wizualizator hashy SSH Randomart:** graficzne generowanie plansz szachowych (Drunken Bishop 9×17) dla skrótów SHA-256.

10. **🌋 Global Seismology & Drum Seismograph (`mod_seismo.py`):
    * **Sejsmograf bębnowy na żywo:** animowany zwój papieru z drgającą igłą rejestrujący wstrząsy sejsmiczne w czasie rzeczywistym.
    * **Trzęsienia ziemi na świecie z USGS:** lista ostatnich zjawisk z magnitudą w skali Richtera, głębokością i odległością w km od użytkownika.
    * **Alert Tsunami NOAA/PTWC:** automatyczny wskaźnik zagrożenia falami przybrzeżnymi przy silnych wstrząsach podwodnych.

11. **🏕️ Tactical Survival & Off-Grid Platform (`mod_survival.py`):
    * **Rozszerzalna baza wiedzy offline:** silnik czytnika ładujący pliki Markdown (`.md`) i JSON z katalogu `data/survival/custom/`.
    * **9 Kategorii Wiedzy:** woda i filtry węglowe, prąd z akumulatora 12V i dynamo, ogień bez zapałek, zima w bloku ("pokój w pokoju"), łączność PMR 3/33, pierwsza pomoc.
    * **Interaktywne kalkulatory:** kalkulator WHO ORS (cukier/sól), magazyn energii baterii, kompas słoneczny z tarczą zegarka, planer zapasów wody, atlas węzłów ratowniczych ASCII.
    * **Awaryjny stroboskop SOS (Przycisk X):** 3 tryby błysków (kod Morse'a SOS, beacon 1Hz, latarka 100%).

12. **🐬 Flipper Zero (`mod_flipper.py`):
    * Bezpośredni podgląd ekranu 128×64 z powiększeniem piksel-w-piksel w pomarańczowej ramce LCD.
    * Bezpośrednie przekazywanie kliknięć D-Pad, OK i BACK do Flippera przez USB/Bluetooth.

13. **👻 Pwngotchi Companion (`mod_pwngotchi.py`):
    * Odbiór na żywo obrazu cyfrowego zwierzaka i statystyk przez Bluetooth PAN (`192.168.44.44:8080`) lub USB.
    * Klawisz **X**: szybka zmiana motywu (*Cyberpunk Neon*, *Retro Amber*, *Matrix Green*, *Classic E-Paper*).

14. **📻 Cyber Radio & Audio Spectrum (`mod_radio.py`):
    * Strumieniowanie stacji: *SomaFM DEF CON*, *Secret Agent*, *Groove Salad*, *Kohina 8-Bit*, *SceneSat*, *Radio Gorzów 95.6 FM*, *Trójka*.
    * **Animowany magnetofon szpulowy (Reel-to-Reel)** i 3 tryby wizualizacji: 32-pasmowy Equalizer, Oscyloskop CRT, Stereo VU-Meter.

15. **🌐 Tactical LAN Discovery & Port Audit (`mod_netscan.py`):
    * Skaner sieci Wi-Fi LAN z bazą producentów MAC OUI (Apple, RPi, ESP32, Flipper, Ubiquiti, Xiaomi).
    * **Histogram latencji PING na żywo** oraz audyt portów SSH (22), HTTP (80), HTTPS (443), MQTT (1883), HASS (8123).

16. **📡 Tactical BLE Radar (`mod_radar.py`):
    * Okrągły radar z obracającą się wiązką 360° i wykrywaniem urządzeń Bluetooth w czasie rzeczywistym.

17. **📶 Wi-Fi Spectrum Analyzer (`mod_wifi.py`):
    * Wykres słupkowy obciążenia 14 kanałów pasma 2.4 GHz oraz tabela punktów dostępowych AP.

18. **🔌 Hardware Pinouts Cheat-Sheet (`mod_pinouts.py`):
    * Baza pinoutów: Raspberry Pi 40-Pin, ESP32 DevKit, Flipper Zero, USB Type-C, DB9 Serial.
    * Kodowanie kolorami magistrali (5V, 3.3V, GND, I2C, SPI, UART, PWM).

19. **🧮 Cyberdeck Hacker & Net Utils (`mod_calc.py`):
    * **Kalkulator podsieci IPv4 & CIDR:** natychmiastowe wyliczanie maski, wildcard, network, broadcast, puli hostów i bitów binarnych dla dowolnego prefiksu `/1` do `/32`.
    * **Konwerter baz Radix:** konwersja wartości w locie na DEC, HEX (`0x...`), BIN, OCT, znaki ASCII i Base64.
    * **Dekoder pasków rezystora:** interaktywny 4-paskowy rezystor z wyliczaniem omów (Ω, kΩ, MΩ) i tolerancji.

20. **📱 Barcode & QR Code Generator (`mod_qr.py`):
    * **2D Kody QR (Wersje 1-6):** generowanie kodów QR bezpośrednio na ekranie IPS w czystym Pythonie (zero zależności pip) z korekcją błędów Reed-Solomon.
    * **1D Kody Kreskowe:** Code 128 (alfanumeryczne kody magazynowe) oraz EAN-13 (kody towarowe).
    * **Baza szablonów:** Wi-Fi Hotspot Auto-Connect (telefon łączy się z Wi-Fi bez wpisywania hasła), linki URL, adresy portfeli krypto Bitcoin/Ethereum, wizytówki vCard i koordynaty ratunkowe GPS SOS.
    * **Tryb Wysokiego Kontrastu (Klawisz X):** 100% białe tło pod kodem gwarantujące natychmiastowe złapanie ostrości przez aparat telefonu.

21. **⏳ Powder & Physics Sandbox (`mod_sandbox.py`):
    * **Interaktywna symulacja Falling Sand / Powder Game (200+ FPS):** automaty komórkowe na siatce fizyki w czasie rzeczywistym.
    * **9 Materiałów i Żywiołów:** Piasek, Woda, Ogień, Proch strzelniczy (reakcja łańcuchowa wybuchów!), Kwas (trawienie materii), Drewno (palne rusztowania), Lawa, Kamień i Iskry.
    * **Pędzel taktyczny gamepada:** sterowanie pozycją D-Padem, ciągłe sypanie pod klawiszem **A**, wybór materiałów **L1 / R1** oraz gotowe sceny demonstracyjne pod **X**.

22. **🏠 Home Assistant Pocket Controller (`mod_hass.py`):
    * Kieszonkowy pilot inteligentnego domu z siatką kafelków 2×4 (oświetlenie, gniazdka z mocą W, termostat, czujniki jakości powietrza).

23. **🔌 UART Serial Monitor (`mod_uart.py`):
    * Kieszonkowy monitor portu szeregowego USB-C (ESP32, Arduino, Raspberry Pi, routery) z regulacją Baud (9600..230400).

24. **🔬 CamScope - Tactical Inspection Cam & Borescope (`mod_camera.py`):
    * Monitor kamer inspekcyjnych (endoskopy USB-C OTG, mikroskopy warsztatowe `/dev/video*`, kamery IP RTSP/MJPEG Wi-Fi oraz syntetyczny symulator inspekcyjny).
    * **5 filtrów wizyjnych (Klawisz X):** *Normal (Kolor)*, *Night Vision Green (Nocny fosfor)*, *Thermal False-Color (Termowizja)*, *Monochrome (Czarno-biały)*, *Edge Detect (Kontury pęknięć i spoin)*.
    * **Pomiary i celowniki (Klawisz Y):** podziałka mikrometryczna (100 µm/px), siatka celownicza, krzyż miliradianów.
    * **Cyfrowy Zoom 1.0x - 4.0x (Klawisze Góra/Dół):** płynne powiększanie badanego obiektu.
    * **Zrzuty zdjęć w pełnej rozdzielczości (Klawisz A):** automatyczny zapis klatek do folderu `/mnt/SDCARD/Photos/` lub `captures/`.

25. **🛠️ Hardware Diagnostic Lab (`mod_diag.py`):
    * **Wizualny tester gamepada TrimUI Brick:** sylwetka konsoli na ekranie 1024×768 podświetlająca w czasie rzeczywistym wciskane przyciski (D-Pad, ABXY, L1, R1, Menu), liczniki kliknięć i dziennik zdarzeń evdev.
    * **Tester martwych pikseli (Dead Pixels):** pełnoekranowe plansze kontrolne (czysta czerń, biel, czerwień, zieleń, błękit, szarość 50%, siatka ostrości, gradient 16-stopniowy).
    * **Tester dźwięku stereo:** badanie balansu kanałów lewego i prawego głośnika.

26. **⚙️ System Telemetry (`mod_system.py`):**
    * Obciążenie 4 rdzeni Cortex-A53, pamięć RAM, temperatura SoC, bateria oraz IP interfejsów sieciowych.

27. **🛍️ BrickStore GitHub App Store (`mod_store.py`):**
    * **Kieszonkowy sklep aplikacji Wi-Fi:** przeglądanie, pobieranie i instalowanie nowych gier, radarów i narzędzi z repozytorium GitHub `kawaczek/brik` bezdotykowo na konsoli.
    * **Instalacja 1-Click (Klawisz A):** automatyczne pobieranie skryptu `.py` i natychmiastowa aktywacja w menu bez restartu. Usuwanie zbędnych modułów klawiszem **X**.

---

## ⚙️ Dynamiczny System Wtyczek i Konfiguracji (`modules.json`)

W BrickDeck OS **kod główny (`brickdeck.py`) jest w 100% zablokowany i niezależny od modułów**. Nie musisz go w ogóle dotykać!

Wszystkimi modułami steruje plik konfiguracyjny [modules.json](file:///home/kawak/brick/Apps/BrickDeck/modules.json):

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

### Korzyści z konfiguracji `modules.json`:
1. **Włączanie / Wyłączanie:** Zmień `"enabled": false`, aby wyłączyć moduł bez usuwania pliku – nie obciąży pamięci RAM ani paska zakładek.
2. **Własna kolejność kart:** Zmieniaj kolejność elementów w liście JSON, a pasek zakładek w BrickDeck dokładnie ją odtworzy.
3. **Auto-Discovery (`"auto_discover": true`):** Wystarczy wrzucić jakikolwiek plik `mod_*.py` do katalogu `modules/`, a BrickDeck przy starcie sam go wykryje, zainicjalizuje i automatycznie dopisze do `modules.json`!

---

## 🛠️ Jak dopisać WŁASNY moduł w 2 minuty?

Wystarczy stworzyć nowy plik np. `modules/mod_mojanapka.py`:

```python
from core.module_base import BaseModule
from core.theme import COLOR_CYBER_CYAN, COLOR_TEXT_PRIMARY

class MojaApkaModule(BaseModule):
    name = "Moje Narzędzie"
    short_name = "MojaApka"
    icon = "🚀"
    accent_color = COLOR_CYBER_CYAN

    def get_hotkey_hints(self):
        return [
            ("L1/R1", "Moduły"),
            ("A", "Zrób Coś"),
            ("B", "Wróć")
        ]

    def render(self, canvas):
        # 1. Rysuj kartę roboczą
        canvas.draw_card(x=32, y=66, w=960, h=634, title="MOJE NOWE NARZĘDZIE", border_color=self.accent_color)
        
        # 2. Rysuj komponenty z canvas
        canvas.draw.text((60, 130), "Witaj w moim własnym module!", fill=COLOR_TEXT_PRIMARY, font=canvas.draw.getfont())
        canvas.draw_gauge(x=60, y=180, w=400, h=16, value=75, max_val=100, label="Poziom mocy", color=COLOR_CYBER_CYAN)

    def handle_input(self, event: str) -> bool:
        if event == "BTN_A":
            print("Kliknięto A w Mojej Apce!")
            return True
        return False
```

**I to wszystko!** Nie musisz edytować żadnych innych plików ani `brickdeck.py`. BrickDeck automatycznie załaduje Twój moduł!

---

## 🌍 Wielojęzyczność i Silnik Tłumaczeń (i18n)

BrickDeck posiada wbudowany silnik wielojęzyczności (`core/i18n.py`) oraz paczki językowe w formacie JSON w folderze [locales/](file:///home/kawak/brick/Apps/BrickDeck/locales):

* 🇵🇱 **Polski (`pl.json`)**
* 🇬🇧 **English (`en.json`)**
* 🇩🇪 **Deutsch (`de.json`)**
* 🇪🇸 **Español (`es.json`)**

### Jak to działa?
1. **Automatyczne wykrywanie języka konsoli (`"locale": "auto"`):**
   * System odczytuje zmienne środowiskowe Linuksa (`LANG`, `LC_ALL`, `LC_MESSAGES`). Jeśli konsola TrimUI Brick jest ustawiona po niemiecku lub angielsku, BrickDeck automatycznie odpala się w tym języku!
2. **Błyskawiczne przełączanie w locie (Klawisz Y):**
   * W module **System Telemetry** naciśnij przycisk **Y**, aby w ułamku sekundy przełączyć język (`Polski` ➔ `English` ➔ `Deutsch` ➔ `Español` ➔ `Auto`). Zmiana jest natychmiast zapamiętywana w [settings.json](file:///home/kawak/brick/Apps/BrickDeck/settings.json).
3. **Dodawanie dowolnego nowego języka przez społeczność:**
   * Aby dodać np. język francuski, wystarczy utworzyć plik `locales/fr.json`. System sam go wykryje i doda do listy wyboru bez pisania ani jednej linijki kodu Python!
4. **Bezpieczny fallback:**
   * Jeśli w danym języku brakuje tłumaczenia jakiegoś klucza, system automatycznie posiłkuje się wersją angielską lub polską, zapobiegając jakimkolwiek błędom.

---

## 🧪 Jak przetestować to już teraz na PC?

Wystarczy wpisać w terminalu:
```bash
python3 /home/kawak/brick/Apps/BrickDeck/brickdeck.py --mode term
```
*Aplikacja wyświetli pełny interfejs w 24-bitowych kolorach ANSI bezpośrednio w oknie Twojego terminala!*
*Używaj klawiszy **Q / E**, aby przełączać moduły na górnym pasku!*

---

## 🚀 Wgrywanie jutro na TrimUI Brick

1. Włóż kartę microSD do komputera.
2. Skopiuj folder `BrickDeck`:
   ```bash
   cp -r /home/kawak/brick/Apps/BrickDeck /sciezka/do/karty_sd/Apps/
   ```
3. Włóż kartę do konsoli TrimUI Brick i włącz zasilanie.
4. Wejdź w menu **Apps** i kliknij ikonę **BrickDeck** – cały system odpali się w pełnej rozdzielczości 1024×768!
