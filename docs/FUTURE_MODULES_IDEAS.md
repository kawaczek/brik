# 💡 Bank Pomysłów na Przyszłe Moduły BrickDeck OS (Zero Dongle / Pure Onboard)

Zbiór pomysłów na moduły zaprojektowane z myślą o wykorzystaniu wyłącznie wbudowanych podzespołów konsoli **TrimUI Brick** (ekran 1024×768, Wi-Fi, głośniki stereo, D-Pad/ABXY, Linux) bez konieczności podłączania jakichkolwiek zewnętrznych dongli USB.

---

## ✅ Wdrożone Moduły (Gotowe w Systemie – 27 Modułów)
1. **🕒 Desk Clock, Screensaver & MZK (`mod_clock.py`)** – Zegar biurkowy, pogoda Open-Meteo i odjazdy na żywo.
2. **🗺️ Gorzów Live Transit Fleet Radar (`mod_mzk_map.py`)** – Mapa taboru komunikacji miejskiej w czasie rzeczywistym.
3. **🌧️ Radar Opadów i Burz (`mod_rain.py`)** – IMGW / RainViewer z animacją klatek radarowych.
4. **🛰️ Global Aerospace & Satellite Radar (`mod_air_radar.py`)** – Globus 3D, orbita ISS i radar ADS-B.
5. **🚢 Marine Traffic & AIS Radar (`mod_marine.py`)** – Radar morski PPI 360°, szlaki morskie, telemetria statków.
6. **⚡ Blitzortung Live Lightning Radar (`mod_blitz.py`)** – Wyładowania atmosferyczne na żywo na świecie.
7. **🌌 Universal Planetarium & ISS Passes (`mod_sky.py`)** – Mapa nieba nocnego, model 3D Księżyca i przeloty ISS.
8. **☀️ NOAA Space Weather & Aurora Oval (`mod_space.py`)** – Wiatr słoneczny DSCOVR, owal zorzy i plamy słoneczne SDO.
9. **🕵️ Tactical Cipher & Enigma Lab (`mod_crypto.py`)** – Pełna Enigma M3, OTP i SSH Randomart.
10. **🌋 Global Seismology & Drum Seismograph (`mod_seismo.py`)** – Sejsmograf bębnowy i trzęsienia ziemi USGS.
11. **🏕️ Tactical Survival & Off-Grid Platform (`mod_survival.py`)** – Rozszerzalna baza wiedzy (.md/.json), kalkulatory ORS/baterii i stroboskop SOS.
12. **🐬 Flipper Zero Pocket Display (`mod_flipper.py`)** – Pilot i podgląd ekranu Flippera.
13. **👻 Pwngotchi Companion (`mod_pwngotchi.py`)** – Cyfrowy zwierzak Wi-Fi i statystyki przez Bluetooth/USB.
14. **📻 Cyber Radio & Audio Spectrum (`mod_radio.py`)** – Radio internetowe, magnetofon szpulowy i equalizer.
15. **🌐 Tactical LAN Discovery & Port Audit (`mod_netscan.py`)** – Skaner sieci, identyfikacja OUI i ping histogram.
16. **📡 Tactical BLE Radar (`mod_radar.py`)** – Okrągły radar urządzeń Bluetooth 360°.
17. **📶 Wi-Fi Spectrum Analyzer (`mod_wifi.py`)** – Obciążenie kanałów pasma 2.4 GHz i wykres AP.
18. **🔌 Hardware Pinouts Cheat-Sheet (`mod_pinouts.py`)** – Baza wyprowadzeń GPIO, USB-C, DB9, ESP32.
19. **🧮 Cyberdeck Hacker & Net Utils (`mod_calc.py`):** Kalkulator podsieci CIDR, bazy Radix, kody paskowe rezystorów.
20. **📱 Barcode & QR Code Generator (`mod_qr.py`):** 2D kody QR (Wi-Fi, URL, BTC, vCard) oraz 1D kody kreskowe Code 128 i EAN-13.
21. **⏳ Powder & Physics Sandbox (`mod_sandbox.py`):** Interaktywna fizyka cząsteczkowa, 9 materiałów, grawitacja, eksplozje i erozja.
22. **🏠 Home Assistant Pocket Controller (`mod_hass.py`)** – Sterowanie przełącznikami i scenami smart home.
23. **🔌 UART Serial Monitor (`mod_uart.py`)** – Terminal szeregowy z konfigurowalnym baudrate.
24. **🔬 CamScope Borescope & Camera (`mod_camera.py`)** – Kamera inspekcyjna USB z regulacją ekspozycji.
25. **🛠️ Hardware Diagnostic Lab (`mod_diag.py`)** – Test przycisków gamepadu, audio stereo i test kolorów ekranu.
26. **⚙️ System Telemetry & i18n (`mod_system.py`)** – Taktowanie CPU, temperatura, RAM, dysk i zmiana języka OS.
27. **🛍️ BrickStore GitHub App Store (`mod_store.py`)** – Wbudowany sklep aplikacji OTA z instalacją jednym przyciskiem przez Wi-Fi z GitHuba.

---

## 📦 Zapisany Bank Pomysłów (Gotowe do Wdrożenia)

### Grupa 1: Bezpieczeństwo, Krypto & System
1. **🛡️ 2FA TOTP Authenticator & Air-Gapped Vault (`mod_auth.py`):**
   * Sprzętowy generator kodów jednorazowych TOTP (RFC 6238) dla kont Google, GitHub, banków, odcięty od sieci (*air-gapped*).
   * Szyfrowanie bazy kluczy AES-256 z kodem PIN, animowany wskaźnik 30-sekundowego cyklu ważności kodu.
2. **🔍 Tactical Hex Inspector & SD Forensics (`mod_hex.py`):**
   * Przeglądarka bajtów plików binarnych (Offset | Hex | ASCII), automatyczne wykrywanie sygnatur Magic Bytes (ELF, PNG, ZIP, SQLite) i hashowanie MD5/SHA256.
3. **🤖 Pocket AI Terminal & Ollama Gateway (`mod_ai.py`):**
   * Klient czatu ze sztuczną inteligencją przez Wi-Fi łączący się z lokalnym serwerem Ollama na domowym PC lub darmowym API (Gemini, Groq) z efektem strumieniowania tekstu na ekranie.

### Grupa 2: Dźwięk & Audio DSP
4. **🎹 8-Bit Cyber Synth & Chiptune Tracker (`mod_synth.py`):**
   * Syntezator dźwięku retro generujący fale bezpośrednio na głośnikach stereo konsoli (kwadrat NES, trójkąt, piła, szum), 16-krokowy tracker perkusyjny i żywy oscyloskop CRT.
5. **📻 Morse Code Audio Trainer & Koch Method (`mod_morse_trainer.py`):**
   * Dźwiękowa nauka odbioru alfabetu Morse'a ze słuchu oficjalną metodą Kocha (regulacja 5–35 WPM) oraz tryb klucza manualnego na przycisku A z automatycznym dekoderem.

### Grupa 3: Elektronika, Nauka & Pomiary
6. **⚡ Electronics Lab & Circuit Designer (`mod_ee_lab.py`):**
   * Kalkulator generatora NE555 (fale i częstotliwość), projektant filtrów pasywnych RC/LC/RLC, dzielniki napięcia z typoszeregu E12/E24, szerokość ścieżek PCB wg IPC-2152.
7. **🧪 ChemLab – Interaktywna Tablica Mendelejewa (`mod_periodic.py`):**
   * 118 pierwiastków z konfiguracją elektronową i właściwościami fizykochemicznymi oraz szybki kalkulator masy molowej dowolnych związków chemicznych.
8. **🌱 Global Air Quality & Smog Radar (`mod_air_quality.py`):**
   * Monitor stężeń pyłów PM2.5, PM10, CO, NO2, O3, SO2 i europejski indeks AQI dla dowolnego miasta na Ziemi.

### Grupa 4: Czas, Kartografia & Gry
9. **🌐 World Clock & Solar Terminator (`mod_worldclock.py`):**
   * Płaska mapa świata z nałożoną w czasie rzeczywistym krzywą dnia i nocy (Solar Terminator), zegary strefowe i wskaźniki otwarcia sesji giełdowych.
10. **📈 Crypto & Currency Ticker (`mod_ticker.py`):**
    * Wykresy świecowe BTC/ETH/SOL oraz kursy walut NBP, indeks Fear & Greed bez obciążania pamięci konsoli.
11. **🗺️ GPX Track Inspector & Outdoor Workout (`mod_tracks.py`):**
    * Wczytywanie plików tras GPS z karty SD, wektorowa mapa, profil wysokościowy terenu, prędkość i statystyki przewyższeń.
12. **🕹️ CHIP-8 Retro Virtual Machine & Game Lab (`mod_chip8.py`):**
    * Działający interpreter wirtualnej maszyny z lat 70., kultowe gry retro (*Pong, Space Invaders, Tetris*) z podglądem rejestrów CPU i pamięci RAM.
13. **🎲 RPG Companion & Hardware Randomness (`mod_dice.py`):**
    * Kości wielościenne (k4 do k100) oparte o entropię procesora `/dev/urandom`, wieloosobowy zegar szachowy i liczniki HP.
14. **📰 Pocket RSS & Tech News Reader (`mod_rss.py`):**
    * Czytnik artykułów technologicznych i cyberbezpieczeństwa (Hacker News, Niebezpiecznik, Sekurak) z trybem czytania offline.

### Grupa 5: Warsztat, Optyka, Radio & Specjalistyczne
15. **🌀 Stroboskopowy Obrotomierz Optyczny RPM (`mod_tachometer.py`):**
    * Bezdotykowy pomiar prędkości obrotowej wentylatorów, wrzecion i silników (60–3600 RPM) przy użyciu stroboskopowego migania ekranu IPS o regulowanej częstotliwości.
16. **🖼️ Steganografia Obrazowa LSB (`mod_stego.py`):**
    * Ukrywanie i odczytywanie zaszyfrowanych wiadomości tekstowych w najmniej znaczących bitach (LSB) grafik PNG/BMP na karcie SD z analizatorem wykrywania steganografii.
17. **🧩 Dzielenie Sekretu Shamira $(k, n)$ (`mod_shamir.py`):**
    * Matematyczny podział klucza prywatnego, frazy seed lub hasła na $N$ części (np. 5), z których dowolne $K$ (np. 3) odtwarza całość – ochrona przed utratą i zdradą.
18. **✈️ Komputer Nawigacyjny Pilota E6B (`mod_e6b.py`):**
    * Cyfrowy suwak nawigacyjny lotnictwa: trójkąt wiatru, znoszenie, Ground Speed, zużycie paliwa, punkt powrotu i wysokość gęstościowa Density Altitude.
19. **📡 SatTrack 3D – Namiar Anten Satelitarnych (`mod_sat_tracker.py`):**
    * Graficzny kalkulator kąta elewacji, azymutu i skręcenia LNB (Skew) dla anten satelitarnych (HotBird, Astra, satelity pogodowe NOAA) z kątomierzem.
20. **🌊 Symulator Wodospadu SDR & Odbiornika Radiowego (`mod_sdr_sim.py`):**
    * Wirtualne radio programowalne z żywym wodospadem FFT, strojeniem po pasmach i generowaniem sygnałów AM/FM/SSB/CW/FT8 na głośnikach.
21. **💾 Wirtualne Karty Perforowane i Dźwięk Kasetowy (`mod_punchcard.py`):**
    * Symulator 80-kolumnowych kart perforowanych IBM w kodzie EBCDIC oraz generator autentycznego pisku modulacji taśm kasetowych retro-komputerów (ZX Spectrum, C64).
22. **🕹️ Silnik Interaktywnych Gier Tekstowych Z-Machine (`mod_zmachine.py`):**
    * Interpreter klasycznych gier przygodowych i powieści interaktywnych (*Zork*, gry Infocom i Inform 7) ze sterowaniem kołowym dostosowanym pod D-Pad.
23. **📋 Cyberdeck Kanban & Task Tracker (`mod_notes.py`):**
    * Tablica zadań Kanban (*To Do* $\rightarrow$ *In Progress* $\rightarrow$ *Done*) i notatnik w czystych plikach tekstowych na karcie SD z techniką Pomodoro.
24. **⏱️ Multi-Timer Laboratoryjny & Metronom (`mod_timer.py`):**
    * 4 niezależne stopery laboratoryjne z międzyczasami, interwały treningowe oraz akustyczny metronom muzyczny (30–280 BPM) z tykaniem na głośnikach.

### Grupa 6: Matematyka, Optyka & Inżynieria
25. **🌀 Eksplorator Fraktali Mandelbrota & Julii (`mod_mandelbrot.py`):**
    * Płynny zoom D-Padem w głąb zbioru Mandelbrota i Julii (do 10^9x), cyberpunkowe palety barw i pomiar liczb zespolonych.
26. **🧬 Automat Komórkowy & Gra w Życie Conwaya (`mod_life.py`):**
    * Symulator ewolucji komórkowej Conway's Game of Life i 1D automatów Wolframa (Reguła 30/110) z biblioteką gliderów i statystykami.
27. **🔭 Kalkulator Optyki Teleskopowej & Astrofotografii (`mod_optics.py`):**
    * Powiększenie, źrenica wyjściowa, pole widzenia FOV, reguła 500/NPF czasu naświetlania gwiazd i kryterium rozdzielczości Dawesa.
28. **📐 Kalkulator Akustyki & Rezonansów Pokoju (`mod_acoustics.py`):**
    * Fale stojące i mody pokoju (Room Modes), czas pogłosu RT60, prędkość dźwięku wg temperatury i opóźnienia kolumn (delay ms).
29. **🎯 Symulator Balistyczny & Trajektorii Rzutu (`mod_ballistics.py`):**
    * Krzywa balistyczna, opór powietrza, opad pocisku (Bullet Drop), energia kinetyczna (Joule) i poprawki na wiatr w MOA / MIL.
30. **🔧 Asystent Mechanika & Baza Kodów OBD-II (`mod_mechanic.py`):**
    * Polska baza kodów błędów OBD-II (P0/P1/B/C/U), kalkulator zamienników opon i odsadzenia ET, momenty dokręcania śrub (Nm).
31. **🏛️ Praski Zegar Astronomiczny – Orloj (`mod_astroclock.py`):**
    * Czas gwiezdny (Sidereal), godziny babilońskie, pozycja Słońca/Księżyca w zodiaku i dokładne zmierzchy astronomiczne.
32. **🔤 Inspektor Znaków Unicode & ASCII UTF-8 (`mod_unicode.py`):**
    * Przeglądarka znaków U+xxxx, ramki pseudograficzne CP437, symbole techniczne, kody UTF-8 i encje HTML.

### Grupa 7: Bateria, Neuro & Narzędzia Inżynieryjne
33. **🔋 Tester Żywotności Baterii & Profiler (`mod_battery_bench.py`):**
    * Rejestruje krzywą rozładowania konsoli (mV w czasie), wylicza faktyczną kondycję baterii 3000 mAh i podaje realny czas pracy.
34. **🎧 Generator Dźwięków Binaural Beats & Szumów (`mod_binaural.py`):**
    * Dźwięki do skupienia i relaksu na słuchawkach: fale mózgowe (Alpha 10Hz, Theta 6Hz) oraz czysty szum różowy, brązowy i biały.
35. **🧠 Trening Pamięci i Refleksu Cyber-Simon (`mod_brain.py`):**
    * Retro gra logiczno-zręcznościowa na przyciskach ABXY: test pamięci sekwencyjnej (w stylu Simon Says) oraz test czasu reakcji w milisekundach.
36. **🧮 Wielki Przelicznik Jednostek Inżynieryjnych (`mod_units.py`):**
    * Błyskawiczna konwersja: ciśnienie (bar, psi, kPa, atm), moment obrotowy (Nm, ft-lb), moc (W, KM, HP), energia (J, cal, kWh) i kąty (stopnie, radiany).
37. **🔐 Multi-Hasher & Generator Haszy w Locie (`mod_hasher.py`):**
    * Wpisujesz słowo -> natychmiastowy podgląd sum: MD5, SHA-1, SHA-256, CRC32, BLAKE2 oraz format Base64.

### Grupa 8: Grafika, Pakiety, Dźwięk & Symulacje
38. **🎨 Pixel Art Studio & Sprite Painter (`mod_pixel.py`):**
    * Kieszonkowy edytor grafiki pikselowej (8x8, 16x16, 32x32) sterowany D-Padem z eksportem do tablic C / Pythona lub PNG.
39. **📡 Wi-Fi Packet Sniffer & DNS Inspector (`mod_sniffer.py`):**
    * Podgląd pakietów w sieci domowej (ARP, zapytania DNS, ICMP, DHCP), wykres przepustowości KB/s i monitor domen.
40. **🎸 Instrument Tuner & Pitch Generator (`mod_tuner.py`):**
    * Stroik muzyczny z generatorem wzorcowych częstotliwości (A4 = 440 Hz / 432 Hz, gitara EADGBE, bas) i animowanym kołem stroboskopowym.
41. **🪐 Symulator Grawitacji N-Ciał & Orbit (`mod_gravity.py`):**
    * Fizyczna symulacja grawitacji układów planetarnych, wystrzeliwanie sond i obserwowanie orbit Keplera na żywo.
42. **🧠 Symulator Maszyny Turinga (`mod_turing.py`):**
    * Wizualny model z przesuwaną taśmą, głowicą i programami (dodawanie binarne, negacja bitów, zajęty bóbr).
43. **🗺️ Subnet CIDR Matrix & IPAM Planner (`mod_ipam.py`):**
    * Klockowa mapa podziału sieci IPv4 na podsieci i VLANy z kontrolą nakładania się zakresów IP.

### Grupa 9: Gry 3D, Wirtualne Zwierzęta & Retro Hacking Games
44. **🕹️ 3D Cyber-Maze & Raycaster (`mod_raycaster.py`):**
    * Prawdziwy silnik 3D Raycasting (60 FPS w czystym Pythonie). Eksploracja korytarzy D-Padem, minimapa, zbieranie dyskietek z danymi i otwieranie grodzi klawiszem A.
45. **👾 CyberPet Pocket Virtual Monster (`mod_tamagotchi.py`):**
    * Wirtualny pikselowy zwierzak/cyber-bot na ekranie. Karmienie, czyszczenie, minigry na przyciskach ABXY, ewolucja i stan zapisywany na karcie SD.
46. **🔓 Safe Cracker & Cyber Lockpicking (`mod_lockpick.py`):**
    * Minigra włamywania do zamków i sejfów szyfrowych: kręcenie tarczą D-Padem, wyczuwanie kliknięć zapadek w głośnikach i łamanie kombinacji na czas.
47. **📠 80s ARPANET BBS & Wardialer (`mod_telehack.py`):**
    * Klimatyczny terminal w stylu filmu WarGames (1983): wardialing numerów modemowych z dźwiękami dial-up, włamywanie na serwery Unix z lat 80., chatbot `eliza` i filmy ASCII.

### Grupa 10: Gry Zręcznościowe, Mechanika Płynów & Rytm
48. **💥 Cyber Artillery & Scorched Earth (`mod_artillery.py`):**
    * Klasyczny pojedynek czołgów 2D z niszczalnym terenem, wiatrem, kątem lufy i arsenałem pocisków (Nuke, MIRV, nalot) vs AI lub 2 graczy na jednym padzie.
49. **🌊 Real-Time Fluid Dynamics (`mod_fluid.py`):**
    * Hipnotyzująca mechanika płynów Naviera-Stokesa w 60 FPS: mieszanie prądów D-Padem, wstrzykiwanie barwników RGB klawiszem A, wiry i opływ przeszkód.
50. **🔌 Circuit Conduit Hacker (`mod_pipe_hack.py`):**
    * Gra logiczno-zręcznościowa w stylu BioShock / Pipemania: obracanie segmentów magistrali i bramek logicznych na czas, by doprowadzić impuls danych do rdzenia.
51. **🎵 Cyber Beat Pocket Tap (`mod_rhythm.py`):**
    * Dynamiczna gra rytmiczna w neonowej oprawie chiptune: spadające nuty na 4 tory (D-Pad / ABXY), combo, oceny celności i pulsujący equalizer w tle.

### Grupa 11: Kosmiczne Gry Fizyczne, Wyścigi & Łamigłówki Optyczne
52. **🚀 Apollo Cyber Lander (`mod_lunar_lander.py`):**
    * Fizyczny symulator lądowania na obcej planecie 2D: ciąg główny pod A, silniki manewrowe RCS D-Padem, ograniczony zbiornik paliwa i lądowanie < 2 m/s.
53. **☄️ Vector Space Combat 360° (`mod_asteroids.py`):**
    * Wektorowy klimat automatów arcade z lat 80.: obrót 360°, bezwładność Newtona, strzały laserowe, skoki w nadprzestrzeń (Hyperspace) i rozbijanie asteroid.
54. **🏎️ Synthwave Vector Highway (`mod_wireframe_race.py`):**
    * Wektorowy wyścig pseudo-3D (OutRun / Night Driver): neonowa trasa, zakręty, pagórki, wymijanie cyber-aut D-Padem i walka z czasem na bramkach checkpoint.
55. **🪞 Laser Matrix & Optics Lab (`mod_laser_optics.py`):**
    * Łamigłówka optyczna: rozmieszczanie zwierciadeł, pryzmatów rozszczepiających kolory RGB i filtrów, by skierować wiązkę lasera do receptorów.

### Grupa 12: Klasyki Arcade, Flipper & Gry Logiczne
56. **🚀 Cyber Defense Interceptor (`mod_missile_command.py`):**
    * Kultowy Missile Command: spadające trajektorie rakiet, celownik D-Padem, wybuchy kasetowe pod A niszczące wrogie pociski w powietrzu.
57. **🕹️ Neon Cyber Pinball (`mod_pinball.py`):**
    * W pełni fizyczny flipper cyfrowy: lewy i prawy flipper pod L1/R1, naciąg sprężyny pod A, rampy, grzybki odbijające i mnożniki punktów.
58. **📦 Cyberdeck Warehouse Sokoban (`mod_sokoban.py`):**
    * Japońska łamigłówka z serwerowni: przepychanie rdzeni zasilających D-Padem, dziesiątki poziomów, licznik ruchów i cofanie pod B.
59. **🧱 Cyber Arkanoid & Vaus Paddle (`mod_breakout.py`):**
    * Dynamiczny rozbijacz bloków: fizyka odbijania kulek, lasery z paletki, multikula x3, niszczenie zbrojonych cyber-cegiełek z cząsteczkami.
