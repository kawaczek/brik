# 🛰️ Encyklopedia Modułów BrickDeck OS (27 Narzędzi)

Kompletna dokumentacja techniczna wszystkich **27 wbudowanych modułów** środowiska BrickDeck OS dla TrimUI Brick. Każdy moduł został zaprojektowany z myślą o ergonomii gamepadu oraz zasadzie **Zero Hardware Requirement** (automatyczny fallback na publiczne internetowe API, gdy brak fizycznego dongla USB).

---

## 📑 Lista Modułów

1. [`mod_clock.py` – Desk Clock, Screensaver & Odjazdy MZK](#1-mod_clockpy--desk-clock-screensaver--odjazdy-mzk)
2. [`mod_mzk_map.py` – Gorzów Live Transit Fleet Radar](#2-mod_mzk_mappy--gorzów-live-transit-fleet-radar)
3. [`mod_rain.py` – Radar Opadów i Burz IMGW / RainViewer](#3-mod_rainpy--radar-opadów-i-burz-imgw--rainviewer)
4. [`mod_air_radar.py` – Global Aerospace & Satellite Radar](#4-mod_air_radarpy--global-aerospace--satellite-radar)
5. [`mod_marine.py` – Global Marine Traffic & AIS Radar](#5-mod_marinepy--global-marine-traffic--ais-radar)
6. [`mod_blitz.py` – Global Lightning Radar (Blitzortung)](#6-mod_blitzpy--global-lightning-radar-blitzortung)
7. [`mod_sky.py` – Universal Planetarium & ISS Passes](#7-mod_skypy--universal-planetarium--iss-passes)
8. [`mod_space.py` – NOAA Space Weather & Aurora Oval](#8-mod_spacepy--noaa-space-weather--aurora-oval)
9. [`mod_crypto.py` – Tactical Cipher & Enigma Lab](#9-mod_cryptopy--tactical-cipher--enigma-lab)
10. [`mod_seismo.py` – Global Seismology & Drum Seismograph](#10-mod_seismopy--global-seismology--drum-seismograph)
11. [`mod_survival.py` – Tactical Survival & Off-Grid Platform](#11-mod_survivalpy--tactical-survival--off-grid-platform)
12. [`mod_flipper.py` – Flipper Zero Pocket Display](#12-mod_flipperpy--flipper-zero-pocket-display)
13. [`mod_pwngotchi.py` – Pwngotchi Companion](#13-mod_pwngotchipy--pwngotchi-companion)
14. [`mod_radio.py` – Cyber Radio & 32-Band Visualizer](#14-mod_radiopy--cyber-radio--32-band-visualizer)
15. [`mod_netscan.py` – Tactical LAN Discovery & Port Audit](#15-mod_netscanpy--tactical-lan-discovery--port-audit)
16. [`mod_radar.py` – Tactical BLE Radar 360°](#16-mod_radarpy--tactical-ble-radar-360)
17. [`mod_wifi.py` – Wi-Fi 2.4 GHz Spectrum Analyzer](#17-mod_wifipy--wi-fi-24-ghz-spectrum-analyzer)
18. [`mod_pinouts.py` – Hardware Pinouts Cheat-Sheet](#18-mod_pinoutspy--hardware-pinouts-cheat-sheet)
19. [`mod_calc.py` – CIDR Subnet & Hacker Utils](#19-mod_calcpy--cidr-subnet--hacker-utils)
20. [`mod_qr.py` – Barcode & QR Code Generator](#20-mod_qrpy--barcode--qr-code-generator)
21. [`mod_sandbox.py` – Powder & Physics Sandbox](#21-mod_sandboxpy--powder--physics-sandbox)
22. [`mod_hass.py` – Home Assistant Pocket Controller](#22-mod_hasspy--home-assistant-pocket-controller)
23. [`mod_uart.py` – UART Serial Monitor](#23-mod_uartpy--uart-serial-monitor)
24. [`mod_camera.py` – CamScope Tactical Borescope & Camera](#24-mod_camerapy--camscope-tactical-borescope--camera)
25. [`mod_diag.py` – Hardware Diagnostic Lab](#25-mod_diagpy--hardware-diagnostic-lab)
26. [`mod_system.py` – System Telemetry & i18n Switcher](#26-mod_systempy--system-telemetry--i18n-switcher)
27. [`mod_store.py` – BrickStore GitHub App Store](#27-mod_storepy--brickstore-github-app-store)

---

### 1. `mod_clock.py` – Desk Clock, Screensaver & Odjazdy MZK
* **Przeznaczenie:** Główny zegar biurkowy, stacja pogodowa i wirtualna tablica przystankowa. Po 60 sekundach bezczynności konsola sama przełącza się w ten tryb jako wygaszacz.
* **Kluczowe funkcje:**
  * Wielki zegar cyfrowy 54pt z pełną polską datą zlokalizowaną przez i18n.
  * Pogoda na żywo z Open-Meteo (temperatura, ikony warunków, siła wiatru, smog PM2.5/PM10).
  * Oficjalne API MZK Gorzów: odjazdy autobusów i tramwajów w czasie rzeczywistym z licznikiem minut i badge'em `>>> ZA CHWILĘ <<<`.
  * Trzy animowane tła w 60 FPS: *3D Starfield* (pole gwiazd w głąb), *Matrix Rain* (zielone japońskie katakany), *Retro Synthwave* (neonowa siatka perspektywiczna).
* **Sterowanie:**
  * `X`: Zmiana aktywnego przystanku (Katedra, AWF, Jagiely, Dworzec Główny, Rondo Santockie, Wieprzyce).
  * `Y`: Przełączanie stylu animacji tła.
  * `A`: Natychmiastowe wymuszenie odświeżenia pogody i odjazdów.

---

### 2. `mod_mzk_map.py` – Gorzów Live Transit Fleet Radar
* **Przeznaczenie:** Wektorowy radar floty komunikacji miejskiej w Gorzowie Wielkopolskim na żywo.
* **Kluczowe funkcje:**
  * Wektorowy zarys miasta Gorzowa: zakole rzeki Warty, główne arterie, pętle Silwana, Piaski, Wieprzyce.
  * Pozycje GPS tramwajów (linie 1, 2, 3 w bursztynie) oraz autobusów (linie 101, 104, 124... w cyjanie).
  * Rysowanie kąta kursu (Bearing) ze strzałkami zwrotu pokazującymi kierunek jazdy każdego pojazdu.
* **Sterowanie:**
  * `D-Pad`: Przesuwanie kamery po mapie miasta.
  * `X / Y`: Przybliżanie / oddalanie mapy (Zoom).
  * `A`: Wycentrowanie widoku na centrum miasta (Katedra).
  * `B`: Przełączanie filtrów (Tylko Tramwaje / Tylko Autobusy / Wszystkie).

---

### 3. `mod_rain.py` – Radar Opadów i Burz IMGW / RainViewer
* **Przeznaczenie:** Ostrzeganie przed burzami i opadami deszczu dla Zachodniej Polski i Ziemi Lubuskiej.
* **Kluczowe funkcje:**
  * Integracja z radarem RainViewer / IMGW – pobieranie klatek odbiciowości radarowej.
  * 8-klatkowa animowana oś czasu: od -60 minut (historia chmur) do +45 minut (prognoza wektora opadu).
  * Kolorowa skala dBZ: od delikatnej mżawki (15 dBZ, błękit) po niebezpieczne burze z gradem (65 dBZ, fiolet).
* **Sterowanie:**
  * `D-Pad Lewo / Prawo`: Ręczne przewijanie klatek w osi czasu.
  * `A`: Pauza / Wznowienie automatycznej animacji radaru.
  * `Y`: Zmiana promienia skanowania (Województwo Lubuskie / Cała Polska).

---

### 4. `mod_air_radar.py` – Global Aerospace & Satellite Radar
* **Przeznaczenie:** Monitorowanie przestrzeni kosmicznej i ruchu lotniczego nad dowolnym miejscem na świecie.
* **Kluczowe funkcje:**
  * **Taktyczny Globus 3D:** Ortograficzna projekcja kuli ziemskiej z południkami, równikiem i obrotem Ziemi.
  * **Satelity na żywo:** Pozycja Międzynarodowej Stacji Kosmicznej (**ISS**) z API `wheretheiss.at` (złoty model z panelami słonecznymi, prędkość 27 600 km/h, pułap 416 km), Tiangong, NOAA-19 oraz Starlink.
  * **Multi-Level Zoom (1.0x do 35.0x):** Płynne zbliżenie od pełnej orbity kosmicznej aż do taktycznego radaru lokalnego ADS-B wykrywającego samoloty nad Twoim miastem.
  * **Wyszukiwarka Lokalizacji:** Geokoder OpenStreetMap Nominatim z kinowym przelotem kamery prosto nad cel.
  * **Ściągawka SDR:** Częstotliwości ISS APRS (145.825 MHz), ISS Voice (145.800 MHz), pasmo lotnicze AM.
* **Sterowanie:**
  * `D-Pad`: Obracanie kuli ziemskiej (szerokość i długość geograficzna).
  * `X / Y`: Płynny zoom (od kosmosu do radaru naziemnego).
  * `B`: Wyszukiwanie miejscowości lub wprowadzenie koordynatów GPS.
  * `A`: Wyśrodkowanie widoku na ISS.

---

### 5. `mod_marine.py` – Global Marine Traffic & AIS Radar
* **Przeznaczenie:** Taktyczny morski radar nawigacyjny PPI 360° oraz monitor ruchu jednostek pływających na żywo (statki handlowe, kontenerowce, tankowce LNG, promy pasażerskie, holowniki, kutry rybackie).
* **Kluczowe funkcje:**
  * **Radar PPI 360°:** Koncentryczne pierścienie zasięgu w milach morskich (2 NM, 5 NM, 10 NM, 25 NM, 50 NM), obracająca się wiązka radaru z poświatą luminoforu, wektorowe kontury linii brzegowej.
  * **Wektory Kursu i Prędkości (COG/SOG):** Statki wyświetlane jako taktyczne groty z 10-minutowym wektorem przewidywanej pozycji, kodowane kolorystycznie według typu (kontenerowce – zieleń, tankowce – czerwień, promy – błękit, holowniki – bursztyn).
  * **Baza Kluczowych Portów i Cieśnin:** Zatoka Pomorska / Świnoujście (baza LNG, tor wodny Szczecin), Zatoka Gdańska (hub DCT, Naftoport), Cieśnina Dover / La Manche, Cieśnina Gibraltarska, Port Rotterdam, Kanał Kiloński, Cieśnina Bosfor, Cieśnina Malakka / Singapur.
  * **Karta Telemetryczna Jednostki:** Pełne dane AIS: nazwa, bandera z flagą, znak wywoławczy Callsign, unikalny numer MMSI, wymiary (długość × szerokość), zanurzenie (draught w metrach), port docelowy i czas przybycia (ETA).
  * **Tabela Floty AIS:** Przewijalna lista wszystkich jednostek w zasięgu radaru z kursem, prędkością w węzłach oraz odległością w milach morskich.
  * **Meteorologia Morska:** Skala wiatru i stanu morza Beauforta (°B), kierunek wiatru i wysokość fal.
* **Sterowanie:**
  * `L1 / R1`: Zmiana portu / akwenu morskiego (Bałtyk, La Manche, Gibraltar, itd.).
  * `D-Pad Góra / Dół`: Przełączanie statku (celowanie reticle `[ ]`).
  * `D-Pad Lewo / Prawo`: Skalowanie zasięgu radaru (Zoom: 2 NM do 50 NM).
  * `X`: Przełącznik widoku (Karta Szczegółowa Statku $\leftrightarrow$ Tabela Floty AIS).
  * `Y`: Odświeżenie danych AIS / symulacji ruchu kinematycznego.
  * `A`: Wyśrodkowanie na jednostce / zatwierdzenie.

---

### 6. `mod_blitz.py` – Global Lightning Radar (Blitzortung)
* **Przeznaczenie:** Monitor wyładowań atmosferycznych i uderzeń piorunów na żywo na całym świecie (Europa, USA, Azja, Ameryka Płd., Afryka, Australia).
* **Kluczowe funkcje:**
  * Wyświetlanie każdego uderzenia pioruna w czasie rzeczywistym z kodowaniem kolorystycznym wieku uderzenia (biały < 1 min, żółty < 5 min, pomarańczowy < 10 min, czerwony > 10 min).
  * Obliczanie odległości do najbliższego uderzenia w kilometrach oraz czasu do nadejścia fali dźwiękowej grzmotu.
  * Ostrzeżenie przed bezpośrednią bliskością burzy (`< 25 km`).
  * Przełączanie regionów: Europa i Polska, Globalny Globus, Ameryka Północna, Azja.
* **Sterowanie:**
  * `D-Pad`: Przesuwanie mapy wyładowań.
  * `X`: Przełącznik dźwiękowych trzasków elektrostatycznych.
  * `Y`: Przełączanie kontynentu / regionu.
  * `A`: Odświeżenie danych stacji TOA.
  * `B`: Centrowanie na bazę użytkownika.

---

### 7. `mod_sky.py` – Universal Planetarium & ISS Passes
* **Przeznaczenie:** Uniwersalna mapa nieba nocnego, model 3D fazy Księżyca oraz predyktor przelotów stacji kosmicznej ISS działający w 100% offline dla dowolnego miejsca na Ziemi.
* **Kluczowe funkcje:**
  * Model 3D Księżyca z realistycznym cieniowaniem terminatora, kraterami i dokładnym procentem oświetlenia tarczy z datą najbliższej pełni.
  * Horyzontalna kopuła nieba 360° z wyliczaniem azymutu i elewacji gwiazd z katalogu (Wega, Syriusz, Betelgeza, Polaris, Rigel, Arktur).
  * Linie gwiazdozbiorów (Wielki Wóz, Trójkąt Letni, Orion) i etykiety gwiazd.
  * Rozpiska widocznych przelotów ISS z pułapem, trasą azymutu i jasnością magnitudo.
  * Przełącznik miast świata (Gorzów, Warszawa, Londyn, Nowy Jork, Tokio, Sydney).
* **Sterowanie:**
  * `D-Pad Lewo / Prawo`: Obrót horyzontu (Azymut).
  * `X`: Włącz / Wyłącz linie gwiazdozbiorów.
  * `Y`: Włącz / Wyłącz etykiety gwiazd.
  * `B`: Zmiana miasta obserwacji (półkula płn / płd).

---

### 8. `mod_space.py` – NOAA Space Weather & Aurora Oval
* **Przeznaczenie:** Globalny monitor pogody kosmicznej, wiatru słonecznego, rozbłysków rentgenowskich i owalu zorzy polarnej z satelitów NASA/NOAA.
* **Kluczowe funkcje:**
  * Złota tarcza Słońca UV 193Å z satelity NASA SDO z naniesionymi aktywnymi grupami plam słonecznych.
  * Biegunowa projekcja owalu zorzy polarnej (Aurora Borealis / Australis) z dynamicznym pierścieniem zależnym od indeksu Kp.
  * Wskaźniki wiatru słonecznego z satelity DSCOVR w punkcie L1: prędkość w km/s, gęstość plazmy i wektor magnetyczny Bz.
  * Skala rozbłysków rentgenowskich GOES X-Ray (klasy A, B, C, M, X) oraz indeks Kp (0–9) z alertem zorzy w Polsce.
* **Sterowanie:**
  * `X`: Przełącznik bieguna (Zorza Północna / Zorza Południowa).
  * `Y`: Pokaż / Ukryj plamy słoneczne.
  * `A`: Odśwież dane z serwerów NOAA SWPC.

---

### 9. `mod_crypto.py` – Tactical Cipher & Enigma Lab
* **Przeznaczenie:** Kieszonkowe laboratorium kryptograficzne i symulator legendarnej wojskowej maszyny szyfrującej Enigma.
* **Kluczowe funkcje:**
  * Wierne historyczne okablowanie rotorów Enigmy M3 (Rotory I, II, III, Reflektor B) z mechanizmem obrotu i łącznicą kablową (Steckerbrett).
  * Animowana tablica żarówek (Glühlampen) zapalająca szyfrowaną literę w czasie rzeczywistym.
  * Taśma dalekopisu (Ticker tape) dzieląca szyfrogram na wojskowe 5-znakowe grupy.
  * Generator absolutnie niełamalnych jednorazowych kluczy One-Time Pad (OTP) z entropii sprzętowej procesora `/dev/urandom`.
  * Wizualizator kluczy SSH Randomart (Drunken Bishop 9×17) dla sum kontrolnych SHA-256.
* **Sterowanie:**
  * `D-Pad`: Nawigacja po klawiaturze maszyny.
  * `A`: Wciśnięcie klawisza (szyfrowanie, obrót bębnów i zapalenie żarówki).
  * `X`: Przełączanie trybu (Enigma / One-Time Pad / SSH Randomart).
  * `Y`: Ręczny obrót bębna szyfrującego.
  * `B`: Usuń ostatni znak / backspace.

---

### 10. `mod_seismo.py` – Global Seismology & Drum Seismograph
* **Przeznaczenie:** Globalny monitor trzęsień ziemi i ruchów płyt tektonicznych na żywo (USGS/EMSC).
* **Kluczowe funkcje:**
  * Animowany sejsmograf bębnowy z papierowym zwojem i drgającym rysikiem rejestrującym mikrosejsmiczne fale gruntu w czasie rzeczywistym.
  * Lista najnowszych trzęsień ziemi na Ziemi z magnitudą Richtera, głębokością ogniska i wyliczoną odległością w km od użytkownika.
  * Kolorystyczne kodowanie siły wstrząsów (od M2.5 w cyjanie po niszczycielskie M6.5+ w neonowym różu).
  * Automatyczny alert zagrożenia falami tsunami (NOAA / PTWC).
* **Sterowanie:**
  * `D-Pad Góra / Dół`: Przeglądanie listy trzęsień ziemi.
  * `A`: Centruj na wybranym epicentrum / Odśwież dane USGS.
  * `X`: Zmień filtr magnitudy (M2.5+ / M4.5+ / M6.0+).
  * `Y`: Włącz / Wyłącz dźwiękowy alarm sejsmiczny.

---

### 11. `mod_survival.py` – Tactical Survival & Off-Grid Platform
* **Przeznaczenie:** Rozszerzalna platforma przetrwania, baza wiedzy i zestaw narzędzi off-grid w sytuacji blackoutu, awarii infrastruktury oraz w terenie. Zbudowana na silniku `SurvivalEngine` (`core/survival_engine.py`) z możliwością natychmiastowego dodawania nowych poradników w Markdown (`.md`) i JSON.
* **Kluczowe funkcje:**
  * **Dynamiczne ładowanie wiedzy:** Automatyczne skanowanie katalogu `Apps/BrickDeck/data/survival/guides/` oraz `data/survival/custom/`. Użytkownik może wrzucić własny plik Markdown ze znacznikami `> [!WARNING]`, krokami i podtytułami, a system natychmiast go wyświetli.
  * **9 Tematycznych Kategorii:** 💧 Woda & Filtracja, ⚡ Energia & Prąd, 🏕️ Schronienie & Zima, 🔥 Ogień & Ciepło, 🧭 Nawigacja, 🆘 Łączność & SOS, 🩹 Pierwsza Pomoc, 🪢 Węzły & Liny, 🍃 Dzika Żywność.
  * **Interaktywny Przybornik Narzędzi (`tools`):**
    * **🧪 Kalkulator WHO ORS:** Oblicza proporcje glukozy i soli dla zadanego litrażu oraz profilu pacjenta (dorosły / dziecko / niemowlę).
    * **🔋 Kalkulator Czasu Pracy Baterii:** Dynamicznie przelicza czas zasilania sprzętu (TrimUI Brick, smartfon, radio) z akumulatora samochodowego 12V 50Ah, AGM, powerbanku lub 18650 ze sprawnością przetwornicy DC-DC 85%.
    * **🧭 Kompas Słoneczny z Tarczą Zegara:** Graficzna tarcza 12-godzinna, rysująca słońce i dwusieczną kąta wyznaczającą oś Północ-Południe (dla czasu letniego i zimowego).
    * **💧 Planer Zapasów Wody:** Oblicza całkowite zapotrzebowanie (litry i kg) na liczbę osób i dni z uwzględnieniem warunków klimatycznych.
    * **🪢 Atlas Węzłów Ratowniczych:** Schematy ASCII i instrukcje 5 kluczowych węzłów (ratowniczy/tatrzański, wyblinka, prusik, szotowy, płaski).
  * **Awaryjny Flasher Optyczny (Przycisk `[X]`):** 3 tryby: pulsujący kod Morse'a SOS (`••• ——— •••`), stroboskop pozycyjny Beacon (1 błysk na 2s), latarka ratunkowa 100% biały ekran.
  * **Hot-Reloading (Przycisk `[Y]`):** Skanowanie i reindeksacja plików `.md` i `.json` w locie bez restartu systemu.
* **Sterowanie:**
  * `L1 / R1`: Przełączanie kategorii bazy wiedzy.
  * `D-Pad Góra / Dół`: Wybór artykułu z listy (lub przewijanie w trybie czytania).
  * `A`: Wejście w tryb pełnego czytania artykułu / akcja w kalkulatorach.
  * `B`: Wyjście z czytnika z powrotem do spisu treści.
  * `X`: Włącz / Wyłącz awaryjny Flasher SOS (lub zmiana parametru w kalkulatorze).
  * `Y`: Skanuj i odśwież bazę poradników (wyszukaj nowe pliki w `custom/`).

---

### 12. `mod_flipper.py` – Flipper Zero Pocket Display
* **Przeznaczenie:** Przenośny ekran i pilot dla Flipper Zero przez USB-C lub BLE.
* **Kluczowe funkcje:**
  * Skalowanie ekranu 128×64 pikseli piksel-w-piksel w pomarańczowej ramce LCD Flippera.
  * Przekazywanie kliknięć przycisków konsoli bezpośrednio do Flippera (Sub-GHz, RFID, NFC, BadUSB).
* **Sterowanie:**
  * `D-Pad`: Krzyżak Flippera.
  * `A`: Przycisk OK.
  * `B`: Przycisk Wróć (Back).

---

### 13. `mod_pwngotchi.py` – Pwngotchi Companion
* **Przeznaczenie:** Monitor stanu cyfrowego zwierzaka do audytu bezpieczeństwa Wi-Fi.
* **Kluczowe funkcje:**
  * Odbiór klatek e-papieru i statystyk przez Bluetooth PAN (`192.168.44.44:8080`) lub USB.
  * Cztery motywy kolorystyczne: *Cyberpunk Neon*, *Retro Amber*, *Matrix Green*, *Classic E-Paper*.
* **Sterowanie:**
  * `X`: Przełączanie motywu wizualnego.
  * `A`: Wymuszenie odświeżenia stanu i nastroju zwierzaka.

---

### 14. `mod_radio.py` – Cyber Radio & 32-Band Visualizer
* **Przeznaczenie:** Kieszonkowy odtwarzacz internetowych stacji radiowych i syntezator audio.
* **Kluczowe funkcje:**
  * Strumienie audio: *SomaFM DEF CON*, *Secret Agent*, *Groove Salad*, *Kohina 8-Bit*, *SceneSat*, *Radio Gorzów 95.6 FM*, *Trójka*.
  * Animowany szpulowiec (Reel-to-Reel Tape Deck) obracający szpule w takt muzyki.
  * 3 tryby wizualizacji: 32-słupkowy analizator widma FFT, zielony oscyloskop CRT i analogowy miernik VU-Meter.
* **Sterowanie:**
  * `D-Pad Góra / Dół`: Wybór stacji radiowej.
  * `A`: Play / Pauza.
  * `X`: Zmiana stylu wizualizacji (Spektrum / Oscyloskop / VU-Meter).

---

### 15. `mod_netscan.py` – Tactical LAN Discovery & Port Audit
* **Przeznaczenie:** Skaner sieci lokalnej Wi-Fi LAN i audytor otwartych portów.
* **Kluczowe funkcje:**
  * Baza producentów MAC OUI (Apple, Raspberry Pi, Espressif ESP32, Flipper Zero, Ubiquiti, Xiaomi).
  * Wykres latencji PING w czasie rzeczywistym.
  * Szybki audyt portów krytycznych: SSH (22), HTTP (80), HTTPS (443), MQTT (1883), Home Assistant (8123).
* **Sterowanie:**
  * `A`: Uruchomienie pełnego skanowania podsieci.
  * `D-Pad Góra / Dół`: Przeglądanie listy wykrytych urządzeń.

---

### 16. `mod_radar.py` – Tactical BLE Radar 360°
* **Przeznaczenie:** Wykrywacz urządzeń Bluetooth Low Energy w otoczeniu.
* **Kluczowe funkcje:**
  * Okrągły radar z obracającą się wiązką fosforową (360° PPI Sweep).
  * Rysowanie punktów (Blips) z intensywnością proporcjonalną do mocy sygnału RSSI.
* **Sterowanie:**
  * `A`: Reskan pasma BLE.
  * `X`: Filtr odległości (Tylko bliskie urządzenia RSSI > -65 dBm).

---

### 17. `mod_wifi.py` – Wi-Fi 2.4 GHz Spectrum Analyzer
* **Przeznaczenie:** Analizator zajętości 14 kanałów pasma ISM 2.4 GHz.
* **Kluczowe funkcje:**
  * Wykres słupkowy obciążenia kanałów 1–14 z zaleceniem najmniej zatłoczonego pasma.
  * Tabela punktów dostępowych z typem szyfrowania (WPA2, WPA3, Otwarta).
* **Sterowanie:**
  * `A`: Odśwież widmo sieci.

---

### 18. `mod_pinouts.py` – Hardware Pinouts Cheat-Sheet
* **Przeznaczenie:** Podręczna baza wyprowadzeń pinów mikrokontrolerów i złączy warsztatowych.
* **Kluczowe funkcje:**
  * Schematy złączy: Raspberry Pi 40-Pin GPIO, ESP32 NodeMCU, Flipper Zero GPIO, USB Type-C 24-Pin, DB9 RS232.
  * Kolorowe kodowanie magistrali (Zasilanie 5V/3.3V, GND, I2C, SPI, UART, PWM).
* **Sterowanie:**
  * `D-Pad Lewo / Prawo`: Wybór płytki / złącza.

---

### 19. `mod_calc.py` – CIDR Subnet & Hacker Utils
* **Przeznaczenie:** Zestaw kalkulatorów sieciowych i elektroniki warsztatowej.
* **Kluczowe funkcje:**
  * **Kalkulator podsieci IPv4 / CIDR:** Obliczanie maski, wildcard, adresu sieci, broadcast, puli hostów i bitów binarnych dla prefiksów od `/1` do `/32`.
  * **Konwerter baz Radix:** Błyskawiczna konwersja wartości w locie na DEC, HEX (`0x...`), BIN, OCT, znaki ASCII i Base64.
  * **Dekoder pasków rezystora:** 4-paskowy interaktywny rezystor wyliczający rezystancję (Ω, kΩ, MΩ) i tolerancję.
* **Sterowanie:**
  * `D-Pad Lewo / Prawo`: Zmiana prefiksu CIDR / paska rezystora.
  * `X`: Przełączanie trybu narzędzia (CIDR / Radix / Rezystor).

---

### 20. `mod_qr.py` – Barcode & QR Code Generator
* **Przeznaczenie:** Generator 2D kodów QR oraz 1D kodów kreskowych (Code 128, EAN-13) zoptymalizowany pod natychmiastowe skanowanie aparatem dowolnego smartfona bezpośrednio z ekranu konsoli.
* **Kluczowe funkcje:**
  * **2D QR Code (Wersje 1–6):** Czysta implementacja w Pythonie (zero zewnętrznych pakietów pip) z korekcją błędów Reed-Solomon (Level L / Level M).
  * **1D Kody Kreskowe:**
    * **Code 128 (Podtyp B):** dowolne ciągi ASCII, numery seryjne i magazynowe czytane przez skanery laserowe.
    * **EAN-13:** standardowe 13-cyfrowe kody towarowe z automatycznym wyliczaniem cyfry kontrolnej modulo-10.
  * **Baza Szablonów (Presets):**
    * Auto-połączenie z Wi-Fi (`WIFI:S:BrickDeck-AP;P:...;;`) – zeskanowanie telefonem natychmiast łączy z siecią bez wpisywania hasła!
    * Linki URL do repozytoriów i stron internetowych.
    * Cyfrowe wizytówki vCard (automatyczny zapis w kontaktach telefonu).
    * Adresy portfeli krypto Bitcoin (SegWit) i Ethereum.
    * Meldunki ratunkowe GPS SOS z koordynatami dla Google/Apple Maps.
  * **Tryb Wysokiego Kontrastu (Klawisz X):** Przełącznik na 100% białe tło gwarantujące natychmiastowe złapanie ostrości przez aparat telefonu nawet w ciemności.
* **Sterowanie:**
  * `L1 / R1`: Przełączanie formatu (QR Code 2D $\leftrightarrow$ Code 128 1D $\leftrightarrow$ EAN-13).
  * `D-Pad Góra / Dół`: Wybór gotowego szablonu z listy.
  * `X`: Przełącznik tła (100% Skaner Biel $\leftrightarrow$ Motyw Cyberdeck).
  * `Y`: Przełącznik poziomu korekcji błędów QR (Level L 7% $\leftrightarrow$ Level M 15%).
  * `A`: Pełny podgląd zawartości zakodowanej w kodzie.

---

### 21. `mod_sandbox.py` – Powder & Physics Sandbox
* **Przeznaczenie:** W pełni interaktywna symulacja fizyki cząsteczkowej (Falling Sand / Powder Game) w czasie rzeczywistym (200+ FPS) zoptymalizowana pod ekran 1024×768 i sterowanie D-Padem.
* **Kluczowe funkcje:**
  * **9 zróżnicowanych materiałów:** Piasek, Woda, Ogień, Proch strzelniczy (reakcja łańcuchowa/wybuchy), Kwas (trawienie materii), Drewno (palne rusztowanie), Lawa, Kamień (niezniszczalna bariera), Iskry.
  * **Fizyka automatów komórkowych:** Grawitacja, przepływ cieczy o różnej gęstości, przewodnictwo cieplne, zapłon, spalanie dymu i parowanie.
  * **Pędzel taktyczny z D-Padem:** Regulowany promień pędzla (1-8 px), ciągłe sypanie pod klawiszem `A` oraz generator predefiniowanych scen (`X`).
* **Sterowanie:**
  * `D-Pad`: Przesuwanie kursora pędzla po planszy.
  * `A`: Sypanie / emiter wybranego materiału.
  * `L1 / R1`: Wybór materiału (Piasek, Woda, Proch, Kwas, Drewno, Lawa...).
  * `X`: Przełączanie gotowych scen (Kaskada lawy, Komora wybuchowa, Zbiornik kwasu).
  * `Y`: Pauza / wznowienie symulacji fizycznej.
  * `B`: Wyczyszczenie planszy (Clear canvas).

---

### 22. `mod_hass.py` – Home Assistant Pocket Controller
* **Przeznaczenie:** Kieszonkowy pilot inteligentnego domu zoptymalizowany pod D-Pad.
* **Kluczowe funkcje:**
  * Siatka kafelków 2×4 (oświetlenie, gniazdka z pomiarem mocy W, termostat, czujniki temperatury i wilgotności).
  * Bezpośrednia komunikacja z Home Assistant REST API.
* **Sterowanie:**
  * `D-Pad`: Nawigacja po siatce urządzeń.
  * `A`: Przełącz stan (Włącz / Wyłącz).

---

### 23. `mod_uart.py` – UART Serial Monitor
* **Przeznaczenie:** Kieszonkowy terminal portu szeregowego USB-C OTG.
* **Kluczowe funkcje:**
  * Podgląd logów startowych ESP32, STM32, Arduino i konsoli u-boot w czasie rzeczywistym.
  * Regulacja prędkości transmisji (Baud: 9600, 19200, 38400, 57600, 115200, 230400).
* **Sterowanie:**
  * `X`: Zmiana prędkości Baud.
  * `A`: Wyczyszczenie bufora konsoli.

---

### 24. `mod_camera.py` – CamScope Tactical Borescope & Camera
* **Przeznaczenie:** Monitor inspekcyjny do endoskopów USB-C OTG, mikroskopów warsztatowych oraz kamer IP.
* **Kluczowe funkcje:**
  * **5 filtrów wizyjnych:** *Normalny (Kolor)*, *Noktowizor (Zielony fosfor)*, *Termowizja (False-color)*, *Monochromatyczny (B&W)*, *Detekcja Krawędzi (Edge detect do pęknięć PCB i spawów)*.
  * **Cyfrowy Zoom 1.0x – 4.0x:** Płynne powiększanie badanej powierzchni.
  * **Celowniki mikrometryczne:** Podziałka w mikrometrach, siatka pomiarowa, krzyż miliradianów.
  * **Zapis zdjęć PNG:** Zrzut klatek w pełnej rozdzielczości do katalogu `/mnt/SDCARD/Photos/` lub `captures/`.
* **Sterowanie:**
  * `A`: Zrób zdjęcie (Snapshot).
  * `X`: Zmiana filtra wizyjnego.
  * `Y`: Przełączanie siatki celowniczej.
  * `D-Pad Lewo / Prawo`: Regulacja cyfrowego zoomu.

---

### 25. `mod_diag.py` – Hardware Diagnostic Lab
* **Przeznaczenie:** Kompleksowy tester podzespołów konsoli TrimUI Brick.
* **Kluczowe funkcje:**
  * **Wizualny tester gamepada:** Rysowana w wektorach sylwetka konsoli podświetlająca w czasie rzeczywistym wciskane przyciski (D-Pad, ABXY, L1, R1, Menu) z licznikami kliknięć i dziennikiem evdev.
  * **Tester martwych pikseli (Dead Pixels):** Pełnoekranowe plansze kontrolne (czysta czerń, biel, czerwień, zieleń, błękit, szarość 50%, siatka ostrości, gradient).
  * **Tester dźwięku stereo:** Badanie balansu kanałów lewego i prawego głośnika konsoli.
* **Sterowanie:**
  * `X`: Przełączanie plansz testera martwych pikseli.
  * `Y`: Uruchomienie testu głośników stereo.

---

### 26. `mod_system.py` – System Telemetry & i18n Switcher
* **Przeznaczenie:** Monitor parametrów życiowych konsoli i przełącznik języka interfejsu.
* **Kluczowe funkcje:**
  * Wykresy obciążenia 4 rdzeni Cortex-A53, pamięci RAM, temperatury SoC i baterii Li-Po.
  * Lista interfejsów sieciowych (`wlan0`, `usb0`, `bnep0`) z adresami IP.
  * **Globalny Przełącznik Języka (i18n):** Błyskawiczna zmiana języka całego systemu na żywo.
* **Sterowanie:**
  * `Y`: Przełącz język (`🇵🇱 Polski` ➔ `🇬🇧 English` ➔ `🇩🇪 Deutsch` ➔ `🇪🇸 Español` ➔ `🌐 Auto`).
  * `A`: Odświeżenie danych telemetrycznych.

---

### 27. `mod_store.py` – BrickStore GitHub App Store
* **Przeznaczenie:** Wbudowany menedżer pakietów i sklep internetowy OTA łączący się przez Wi-Fi z repozytorium GitHub (`kawaczek/brik`).
* **Kluczowe funkcje:**
  * **Pobieranie i instalacja 1-Click (`A`):** Pobiera pliki modułów `.py` bezpośrednio z chmury do `Apps/BrickDeck/modules/` i automatycznie aktywuje je w `modules.json` bez restartu systemu.
  * **Katalog online z kategoriami:** Przeglądanie gier, cyber-narzędzi, komunikacji i symulacji z filtrowaniem (`L1` / `R1`).
  * **Zarządzanie modułami:** Usuwanie niepotrzebnych aplikacji (`X`), aktualizacja wersji i lokalna pamięć podręczna offline.
* **Sterowanie:**
  * `D-Pad Góra / Dół`: Wybór modułu z listy.
  * `L1 / R1`: Przełączanie kategorii.
  * `A`: Zainstaluj lub zaktualizuj moduł z GitHuba.
  * `X`: Odinstaluj wybrany moduł (zwalnia pamięć).
  * `Y`: Wymuś odświeżenie katalogu z GitHuba.
