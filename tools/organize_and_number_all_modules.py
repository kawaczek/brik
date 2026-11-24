#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/organize_and_number_all_modules.py
Renames and organizes all 86 modules with 001..086 3-digit prefixes,
creates symlinks for legacy compatibility, updates registry.json,
and generates screenshots for all 86 modules.
"""

import os
import sys
import shutil
import json
import glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(REPO_ROOT, "Apps", "BrickDeck", "modules")
STORE_DIR = os.path.join(REPO_ROOT, "store", "modules")
REGISTRY_PATH = os.path.join(REPO_ROOT, "store", "registry.json")
SCREENSHOTS_DIR = os.path.join(REPO_ROOT, "docs", "screenshots")

os.makedirs(STORE_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# 86 Canonical Modules Definition in Exact Order
MODULES_LIST = [
    # 001 - 027 (Base Modules)
    {"num": "001", "id": "mod_clock", "name": "Desk Clock, Weather & MZK Radar", "cat": "Narzędzia & Net", "desc": "Zegar biurkowy, wygaszacz ekranu, pogoda Open-Meteo i odjazdy komunikacji miejskiej MZK na żywo.", "ctrl": "D-Pad Lewo/Prawo: Ekrany | A: Odśwież | Y: Konfiguracja"},
    {"num": "002", "id": "mod_mzk_map", "name": "Gorzów Live Fleet Transit Radar", "cat": "Narzędzia & Net", "desc": "Wektorowa mapa taboru komunikacji miejskiej w czasie rzeczywistym z pozycjami GPS autobusów i tramwajów.", "ctrl": "D-Pad: Przesuń Mapę | L1/R1: Zoom | A: Śledź Pojazd"},
    {"num": "003", "id": "mod_rain", "name": "Live Rain & Storm Radar (IMGW)", "cat": "Narzędzia & Net", "desc": "Radar opadów i chmur deszczowych IMGW / RainViewer z animacją klatek czasowych w pętli.", "ctrl": "D-Pad: Przesuń Mapę | A: Start/Pauza Animacji | L1/R1: Zoom"},
    {"num": "004", "id": "mod_air_radar", "name": "Global Aerospace & Satellite Radar", "cat": "Nauka & Kosmos", "desc": "Globus 3D, orbita stacji ISS, przeloty satelitów i radar ruchu lotniczego ADS-B OpenSky.", "ctrl": "D-Pad: Obrót Globusa | L1/R1: Zoom | A: Wybierz Samolot"},
    {"num": "005", "id": "mod_marine", "name": "Marine Traffic & AIS Radar", "cat": "Narzędzia & Net", "desc": "Radar morski PPI 360°, szlaki żeglugowe, telemetria statków morskich i tankowców.", "ctrl": "D-Pad: Przesuń Sektor | L1/R1: Zasięg Mili Morskich | A: Dane Statku"},
    {"num": "006", "id": "mod_blitz", "name": "Live Lightning Radar (Blitzortung)", "cat": "Nauka & Kosmos", "desc": "Rejestracja wyładowań atmosferycznych i burz na żywo na świecie z detekcją fali uderzeniowej.", "ctrl": "D-Pad: Przesuń Mapę | L1/R1: Skala | A: Filtr Wyładowań"},
    {"num": "007", "id": "mod_sky", "name": "Universal Planetarium & ISS Passes", "cat": "Nauka & Kosmos", "desc": "Interaktywna mapa nieba nocnego, gwiazdozbiory, model 3D Księżyca i trajektorie ISS.", "ctrl": "D-Pad: Obrót Nieba | L1/R1: FOV | A: Informacje o Gwieździe"},
    {"num": "008", "id": "mod_space", "name": "NOAA Space Weather & Aurora Oval", "cat": "Nauka & Kosmos", "desc": "Wiatr słoneczny z sondy DSCOVR, owal zorzy polarnej i plamy słoneczne z satelity SDO.", "ctrl": "D-Pad: Przegląd Wykresów | A: Odśwież Dane NOAA"},
    {"num": "009", "id": "mod_crypto", "name": "Tactical Cipher & Enigma Lab", "cat": "Cyber & Hacking", "desc": "Pełny symulator wojskowej maszyny szyfrującej Enigma M3, One-Time Pad i SSH Randomart.", "ctrl": "D-Pad: Wirniki Enigmy | ABXY: Klawiatura Szyfrująca | Y: Łącznica"},
    {"num": "010", "id": "mod_seismo", "name": "Global Seismology & Drum Seismograph", "cat": "Nauka & Kosmos", "desc": "Bębnowy sejsmograf z wstrząsami sejsmicznymi USGS na żywo i wykres fal P i S.", "ctrl": "D-Pad: Wybór Trzęsienia Ziemi | A: Szczegóły Epicentrum"},
    {"num": "011", "id": "mod_survival", "name": "Tactical Survival & Off-Grid Manual", "cat": "Narzędzia & Net", "desc": "Rozszerzalna baza wiedzy offline, kalkulatory przetrwania, woda, schronienie i stroboskop SOS.", "ctrl": "D-Pad: Przeglądanie Artykułów | A: Czytaj | Y: Sygnał SOS"},
    {"num": "012", "id": "mod_flipper", "name": "Flipper Zero Pocket Display", "cat": "Cyber & Hacking", "desc": "Zdalny podgląd ekranu Flippera Zero, pilot sterowania i telemetria przez USB/UART.", "ctrl": "D-Pad: Nawigacja Flippera | A: Klawisz OK | B: Back"},
    {"num": "013", "id": "mod_pwngotchi", "name": "Pwngotchi Companion", "cat": "Cyber & Hacking", "desc": "Cyfrowy zwierzak Wi-Fi, nastroje, przechwycone uściski dłoni EAPOL i statystyki.", "ctrl": "D-Pad: Przegląd Kanałów | A: Zmień Twarz | Y: Zapisz PCAP"},
    {"num": "014", "id": "mod_radio", "name": "Cyber Radio & Audio Spectrum", "cat": "Multimedia & Audio", "desc": "Radio internetowe, retro magnetofon szpulowy i 32-pasmowy spektrogram audio FFT.", "ctrl": "D-Pad Lewo/Prawo: Zmiana Stacji | A: Play/Pause | L1/R1: Głośność"},
    {"num": "015", "id": "mod_netscan", "name": "Tactical LAN Discovery & Port Audit", "cat": "Cyber & Hacking", "desc": "Szybki audyt urządzeń w podsieci Wi-Fi, identyfikacja vendorów OUI i skaner otwartych portów.", "ctrl": "D-Pad: Przewijaj Hosty | A: Skanuj Porty | Y: Ping Histogram"},
    {"num": "016", "id": "mod_radar", "name": "Tactical BLE Radar 360°", "cat": "Cyber & Hacking", "desc": "Okrągły radar urządzeń Bluetooth Low Energy, odległość szacowana z RSSI i Apple AirTags.", "ctrl": "D-Pad: Zmiana Sektora | A: Szczegóły BLE | X: Filtr UUID"},
    {"num": "017", "id": "mod_wifi", "name": "Wi-Fi Spectrum & Channel Load", "cat": "Cyber & Hacking", "desc": "Analizator obciążenia pasma 2.4 GHz, wykresy interferencji kanałów i monitor sieci SSID.", "ctrl": "D-Pad: Wybór Sieci Wi-Fi | A: Monitor RSSI w Czasie"},
    {"num": "018", "id": "mod_pinouts", "name": "Hardware Pinouts Cheat-Sheet", "cat": "Narzędzia & Net", "desc": "Kieszonkowa baza wyprowadzeń pinów: Raspberry Pi GPIO, USB-C, DB9 RS232, ESP32, ATX.", "ctrl": "D-Pad: Wybór Złącza | L1/R1: Kategoria | A: Podgląd Pinoutu"},
    {"num": "019", "id": "mod_calc", "name": "Hacker Subnet & Radix Calculator", "cat": "Cyber & Hacking", "desc": "Kalkulator podsieci CIDR, przelicznik baz liczbowych HEX/BIN/DEC i kody paskowe rezystorów.", "ctrl": "D-Pad: Wprowadzanie Wartości | ABXY: Zmiana Podsieci CIDR"},
    {"num": "020", "id": "mod_qr", "name": "Barcode & QR Code Generator", "cat": "Narzędzia & Net", "desc": "Generator kodów 2D (Wi-Fi, Bitcoin, vCard, URL) oraz 1D kodów kreskowych Code 128 i EAN-13.", "ctrl": "D-Pad: Wybór Szablonu | A: Generuj Nowy Kod | Y: Zapisz PNG"},
    {"num": "021", "id": "mod_sandbox", "name": "Powder & Physics Particle Sandbox", "cat": "Gry & 3D", "desc": "Interaktywna symulacja fizyki cząsteczkowej: 9 materiałów (piasek, woda, ogień, proch, lawa).", "ctrl": "D-Pad: Kursor | A: Rysuj Materiał | X: Zmiana Cząstki | B: Czyść"},
    {"num": "022", "id": "mod_hass", "name": "Home Assistant Pocket Controller", "cat": "Narzędzia & Net", "desc": "Sterowanie urządzeniami inteligentnego domu, przełączniki światła, termostaty i sceny.", "ctrl": "D-Pad: Wybór Encji | A: Włącz/Wyłącz | Y: Odśwież Stan"},
    {"num": "023", "id": "mod_uart", "name": "UART Serial Monitor & Terminal", "cat": "Cyber & Hacking", "desc": "Konsola portu szeregowego UART z konfigurowalnym baudrate (9600-115200) i buforem logów.", "ctrl": "D-Pad: Przewijaj Bufor | A: Wyślij Pakiet | X: Zmiana Baudrate"},
    {"num": "024", "id": "mod_camera", "name": "CamScope Borescope & USB Camera", "cat": "Narzędzia & Net", "desc": "Podgląd z kamery inspekcyjnej endoskopowej USB na ekranie konsoli z regulacją ekspozycji.", "ctrl": "D-Pad: Regulacja Jasności | A: Zrób Zdjęcie na SD | X: Zoom"},
    {"num": "025", "id": "mod_diag", "name": "Hardware Diagnostic Lab", "cat": "Narzędzia & Net", "desc": "Tester przycisków gamepadu, audio stereo, dead pikseli i kalibracji wyświetlacza IPS.", "ctrl": "Wciskaj dowolne klawisze | L1/R1: Test Dźwięku | Y: Test Barw"},
    {"num": "026", "id": "mod_system", "name": "System Telemetry & i18n Settings", "cat": "Narzędzia & Net", "desc": "Taktowanie CPU, temperatura procesora Allwinner A133P, zużycie RAM i zmiana języka OS.", "ctrl": "D-Pad: Wybór Opcji | A: Zmień Język (PL/EN) | Y: Profil Zasilania"},
    {"num": "027", "id": "mod_store", "name": "BrickStore GitHub App Store", "cat": "Narzędzia & Net", "desc": "Oficjalny wbudowany sklep aplikacji OTA z instalacją jednym przyciskiem przez Wi-Fi z GitHuba.", "ctrl": "D-Pad: Przeglądaj Katalog | A: Zainstaluj Moduł | Y: Odśwież Sklep"},

    # 028 - 045 (Store Batch 1 & 2)
    {"num": "028", "id": "mod_raycaster", "name": "3D Cyber-Maze Raycaster", "cat": "Gry & 3D", "desc": "Trójwymiarowy silnik Raycasting 3D czasu rzeczywistego (60 FPS), zoom minimapy i duże czcionki.", "ctrl": "D-Pad: Ruch | Y: Ustawienia/Czcionka | X: Radar | L1/R1: Zoom"},
    {"num": "029", "id": "mod_artillery", "name": "Cyber Artillery (Tank Wars)", "cat": "Gry & 3D", "desc": "Klasyczny pojedynek czołgów 2D z niszczalnym terenem, wiatrem, kątem lufy i arsenałem pocisków.", "ctrl": "D-Pad Góra/Dół: Kąt | Lewo/Prawo: Moc | L1/R1: Broń | A: Ognia"},
    {"num": "030", "id": "mod_lockpick", "name": "Safe Cracker & Lockpicking", "cat": "Cyber & Hacking", "desc": "Symulator włamywania do zamków i sejfów szyfrowych. Kręcenie tarczą i wyczuwanie zapadek.", "ctrl": "D-Pad Lewo/Prawo: Obrót Tarczy | A: Test Zapadki | B: Reset"},
    {"num": "031", "id": "mod_tamagotchi", "name": "CyberPet Pocket Virtual Monster", "cat": "Gry & 3D", "desc": "Wirtualny pikselowy zwierzak. Karmienie, czyszczenie, zabawa na ABXY i stan na karcie SD.", "ctrl": "D-Pad: Wybór Akcji | A: Nakarm/Baw się | B: Statystyki"},
    {"num": "032", "id": "mod_pipe_hack", "name": "Circuit Conduit Hacker", "cat": "Cyber & Hacking", "desc": "Układanie magistrali danych z obracanych segmentów i bramek logicznych pod presją czasu.", "ctrl": "D-Pad: Kursor | A: Obróć Segment | X: Przyspiesz Przepływ"},
    {"num": "033", "id": "mod_lunar_lander", "name": "Apollo Cyber Lander", "cat": "Gry & 3D", "desc": "Fizyczny symulator lądowania na obcej planecie 2D z grawitacją i ograniczonym paliwem.", "ctrl": "A: Ciąg Główny | D-Pad Lewo/Prawo: Silniki RCS"},
    {"num": "034", "id": "mod_asteroids", "name": "Vector Space Combat 360°", "cat": "Gry & 3D", "desc": "Wektorowy klimat arcade: obrót 360°, bezwładność Newtona, strzały laserowe i rozbijanie skał.", "ctrl": "D-Pad Lewo/Prawo: Obrót | Góra: Ciąg | A: Laser | B: Hyperspace"},
    {"num": "035", "id": "mod_synth", "name": "8-Bit Cyber Synth & Tracker", "cat": "Multimedia & Audio", "desc": "Syntezator dźwięku retro z falami NES, 16-krokowy tracker perkusyjny i żywy oscyloskop.", "ctrl": "D-Pad: Krok | A: Przełącz Nutę | L1/R1: Ścieżka | Y: Start/Stop"},
    {"num": "036", "id": "mod_life", "name": "Conway's Game of Life & Cellular Automata", "cat": "Nauka & Kosmos", "desc": "Symulator ewolucji komórkowej Conway's Game of Life z biblioteką gliderów i statystykami.", "ctrl": "A: Krok/Run | X: Losuj Nową Zupę | D-Pad: Przesuń Siatkę"},
    {"num": "037", "id": "mod_mandelbrot", "name": "Mandelbrot & Julia Fractal Explorer", "cat": "Nauka & Kosmos", "desc": "Płynny zoom D-Padem w głąb zbioru Mandelbrota i Julii, palety barw i pomiar liczb zespolonych.", "ctrl": "D-Pad: Przesuń Kamerę | L1/R1: Zoom In/Out | X: Zmień Paletę"},
    {"num": "038", "id": "mod_auth", "name": "2FA TOTP Authenticator Vault", "cat": "Cyber & Hacking", "desc": "Sprzętowy generator kodów jednorazowych TOTP odcięty od sieci (air-gapped) z szyfrowaniem.", "ctrl": "D-Pad Góra/Dół: Wybór Konta | A: Pokaż Kod TOTP | Y: Dodaj Klucz"},
    {"num": "039", "id": "mod_dice", "name": "RPG Companion & Hardware Randomness", "cat": "Gry & 3D", "desc": "Kości wielościenne (k4-k100) oparte o entropię procesora, zegar szachowy i liczniki HP.", "ctrl": "D-Pad: Wybór Kości | A: Rzut Kością | B: Reset Liczników"},
    {"num": "040", "id": "mod_breakout", "name": "Cyber Arkanoid & Vaus Paddle", "cat": "Gry & 3D", "desc": "Dynamiczny rozbijacz bloków: fizyka odbijania kulek, lasery, multikula x3 i niszczenie cegiełek.", "ctrl": "D-Pad Lewo/Prawo: Ruch Paletką | A: Wystrzel Piłkę | B: Laser"},
    {"num": "041", "id": "mod_pinball", "name": "Neon Cyber Pinball", "cat": "Gry & 3D", "desc": "W pełni fizyczny flipper: lewa i prawa łapka pod L1/R1, naciąg sprężyny pod A i grzybki zderzakowe.", "ctrl": "L1: Lewy Flipper | R1: Prawy Flipper | A: Naciąg Sprężyny"},
    {"num": "042", "id": "mod_sokoban", "name": "Cyberdeck Warehouse Sokoban", "cat": "Gry & 3D", "desc": "Japońska łamigłówka z serwerowni: przepychanie rdzeni zasilających D-Padem, cofanie ruchów.", "ctrl": "D-Pad: Ruch Magazynierem | B: Cofnij Ruch | Y: Restart Poziomu"},
    {"num": "043", "id": "mod_periodic", "name": "ChemLab Periodic Table & Mass Calc", "cat": "Nauka & Kosmos", "desc": "118 pierwiastków z konfiguracją elektronową i kalkulator masy molowej związków chemicznych.", "ctrl": "D-Pad: Nawigacja po Układzie | A: Karta Pierwiastka | Y: Masa Związku"},
    {"num": "044", "id": "mod_ee_lab", "name": "Electronics Lab & NE555 Designer", "cat": "Nauka & Kosmos", "desc": "Kalkulator układu NE555, projektant filtrów pasywnych RC/LC i dzielniki napięcia z typoszeregu E24.", "ctrl": "D-Pad: Zmiana Elementu R/C | A: Wybór Trybu (NE555 / Filtr)"},
    {"num": "045", "id": "mod_hex", "name": "Tactical Hex & SD Forensics", "cat": "Cyber & Hacking", "desc": "Przeglądarka bajtów plików binarnych (Offset | Hex | ASCII) i wykrywanie sygnatur Magic Bytes.", "ctrl": "D-Pad: Przewijaj Bajty | L1/R1: Strona | A: Suma SHA-256"},

    # 046 - 086 (Batch 3, 4, 5, 6 New Modules!)
    {"num": "046", "id": "mod_ai", "name": "Pocket AI Terminal & Ollama Gateway", "cat": "Cyber & Hacking", "desc": "Klient sztucznej inteligencji przez Wi-Fi łączący się z lokalnym serwerem Ollama / vLLM / Gemini.", "ctrl": "D-Pad Góra/Dół: Zmiana Modelu | A: Wyślij Prompt | B: Czyść"},
    {"num": "047", "id": "mod_morse_trainer", "name": "Morse Code Audio Trainer (Koch)", "cat": "Multimedia & Audio", "desc": "Dźwiękowa nauka alfabetu Morse'a ze słuchu metodą Kocha i tryb klucza manualnego.", "ctrl": "D-Pad Lewo/Prawo: Tempo WPM | A: Odsłuch/Kluczuj | Y: Lekcja"},
    {"num": "048", "id": "mod_air_quality", "name": "Global Air Quality & Smog Radar AQI", "cat": "Narzędzia & Net", "desc": "Monitor stężeń pyłów PM2.5, PM10, CO, NO2 i europejski indeks czystości powietrza AQI.", "ctrl": "D-Pad: Zmiana Miasta | A: Odśwież Stację GIOŚ"},
    {"num": "049", "id": "mod_worldclock", "name": "World Clock & Solar Terminator", "cat": "Narzędzia & Net", "desc": "Płaska mapa świata z nałożoną w czasie rzeczywistym krzywą dnia i nocy oraz zegary strefowe.", "ctrl": "D-Pad: Przewijaj Strefy | A: Dodaj Miasto | X: Format 12h/24h"},
    {"num": "050", "id": "mod_ticker", "name": "Crypto & Currency Ticker (NBP)", "cat": "Narzędzia & Net", "desc": "Wykresy świecowe BTC/ETH/SOL, kursy średnie walut NBP i indeks Fear & Greed na żywo.", "ctrl": "D-Pad: Wybór Pary | A: Wybierz Aktywo | X: Zakres 24h/7d"},
    {"num": "051", "id": "mod_tracks", "name": "GPX Track Inspector & Outdoor Workout", "cat": "Narzędzia & Net", "desc": "Wczytywanie tras GPS z karty SD, wektorowa mapa, profil wysokościowy i statystyki.", "ctrl": "D-Pad: Przewijaj Trasę | A: Otwórz GPX | Y: Zoom Mapy"},
    {"num": "052", "id": "mod_chip8", "name": "CHIP-8 Retro Virtual Machine", "cat": "Gry & 3D", "desc": "Interpreter wirtualnej maszyny z grami Pong, Tetris, Invaders oraz podgląd rejestrów CPU.", "ctrl": "D-Pad: Ruch w Grze | A: Akcja | Y: Wybór ROMu CHIP-8"},
    {"num": "053", "id": "mod_rss", "name": "Pocket RSS & Tech News Reader", "cat": "Narzędzia & Net", "desc": "Czytnik artykułów technologicznych i cyberbezpieczeństwa (Niebezpiecznik, Sekurak, HN).", "ctrl": "D-Pad Góra/Dół: Zmiana Artykułu | A: Czytaj | Y: Sync"},
    {"num": "054", "id": "mod_tachometer", "name": "Stroboscopic Optical Tachometer RPM", "cat": "Nauka & Kosmos", "desc": "Bezdotykowy pomiar obrotów wentylatorów i silników stroboskopowym miganiem ekranu IPS.", "ctrl": "D-Pad Lewo/Prawo: ±10 RPM | Góra/Dół: ±100 RPM | A: Stroboskop"},
    {"num": "055", "id": "mod_stego", "name": "Image Steganography LSB Lab", "cat": "Cyber & Hacking", "desc": "Ukrywanie i odczytywanie tajnych wiadomości w bitach grafik PNG z analizatorem Chi-Square.", "ctrl": "D-Pad: Wybór Obrazu | A: Ekstrakcja LSB | Y: Ukryj Tekst"},
    {"num": "056", "id": "mod_shamir", "name": "Shamir Secret Sharing (k, n) Vault", "cat": "Cyber & Hacking", "desc": "Dzielenie klucza prywatnego lub seeda na N części, z których dowolne K odtwarza całość.", "ctrl": "D-Pad: Wybór Części | A: Wprowadź Klucz | Y: Nowy Podział"},
    {"num": "057", "id": "mod_e6b", "name": "E6B Flight Computer & Navigation", "cat": "Narzędzia & Net", "desc": "Cyfrowy suwak lotniczy: trójkąt wiatru, kąt znoszenia, Ground Speed, paliwo i punkt PNR.", "ctrl": "D-Pad Góra/Dół: Prędkość TAS | Lewo/Prawo: Kurs | A: Wiatr"},
    {"num": "058", "id": "mod_sat_tracker", "name": "SatTrack 3D Satellite Dish Pointer", "cat": "Narzędzia & Net", "desc": "Graficzny kalkulator kąta elewacji, azymutu i skręcenia LNB dla anten satelitarnych.", "ctrl": "D-Pad: Wybór Satelity | A: Kalibruj Kompas | X: Pozycja GPS"},
    {"num": "059", "id": "mod_sdr_sim", "name": "SDR Waterfall & Spectrum Simulator", "cat": "Multimedia & Audio", "desc": "Wirtualne radio programowalne z żywym wodospadem FFT i strojeniem po pasmach AM/FM/SSB.", "ctrl": "D-Pad Lewo/Prawo: ±12.5 kHz | Góra/Dół: ±1 MHz | A: Modulacja"},
    {"num": "060", "id": "mod_punchcard", "name": "IBM Punchcard & Cassette Audio Synth", "cat": "Multimedia & Audio", "desc": "Symulator 80-kolumnowych kart perforowanych IBM oraz pisk taśm ZX Spectrum / C64.", "ctrl": "D-Pad: Zmiana Tekstu | A: Pisk Taśmy | X: Zapisz na SD"},
    {"num": "061", "id": "mod_zmachine", "name": "Z-Machine Interactive Fiction (Zork)", "cat": "Gry & 3D", "desc": "Interpreter klasycznych tekstowych gier przygodowych Infocom ze sterowaniem kołowym D-Padem.", "ctrl": "D-Pad Lewo/Prawo: Wybór Komendy | A: Wykonaj | B: Cofnij"},
    {"num": "062", "id": "mod_notes", "name": "Cyberdeck Kanban & Task Tracker", "cat": "Narzędzia & Net", "desc": "Tablica zadań Kanban (To Do -> In Progress -> Done) i notatnik w czystych plikach .txt.", "ctrl": "D-Pad: Przejdź Między Zadaniami | A: Przesuń w Prawo | B: Usuń"},
    {"num": "063", "id": "mod_timer", "name": "Multi-Timer Lab & Acoustic Metronome", "cat": "Narzędzia & Net", "desc": "4 niezależne stopery laboratoryjne z dokładnością 0.1s oraz metronom akustyczny na głośnikach.", "ctrl": "D-Pad: Wybór Stopera | A: Start/Stop | B: Reset | Y: Czas"},
    {"num": "064", "id": "mod_optics", "name": "Telescope Optics & Astrophotography", "cat": "Nauka & Kosmos", "desc": "Powiększenie, źrenica wyjściowa, pole widzenia FOV i reguła 500/NPF czasu naświetlania gwiazd.", "ctrl": "D-Pad Góra/Dół: Okular | Lewo/Prawo: Apertura | A: Sensor"},
    {"num": "065", "id": "mod_acoustics", "name": "Room Acoustics & Axial Modes Calc", "cat": "Multimedia & Audio", "desc": "Fale stojące w pokoju, mody osiowe, czas pogłosu RT60 i opóźnienia kolumn (speaker delay ms).", "ctrl": "D-Pad: Wymiary Pokoju | A: Temperatura | X: Wykres RT60"},
    {"num": "066", "id": "mod_ballistics", "name": "Ballistics Lab & Trajectory Simulator", "cat": "Nauka & Kosmos", "desc": "Krzywa balistyczna pocisków, opór powietrza, opad (Bullet Drop) i poprawki celownika MOA/MIL.", "ctrl": "D-Pad: Dystans | A: Kaliber (.223/.308/6.5CM) | Y: Wiatr"},
    {"num": "067", "id": "mod_mechanic", "name": "Mechanic Assistant & OBD-II Codes", "cat": "Narzędzia & Net", "desc": "Baza kodów błędów OBD-II (P0/P1/B/C/U), kalkulator zamienników opon i momenty śrub.", "ctrl": "D-Pad: Wybór Kodu Błędu | A: Szukaj | Y: Kalkulator Opon"},
    {"num": "068", "id": "mod_astroclock", "name": "Prague Astronomical Clock (Orloj)", "cat": "Nauka & Kosmos", "desc": "Czas gwiezdny LST, godziny babilońskie, pozycja Słońca i Księżyca w znakach zodiaku.", "ctrl": "D-Pad: Przewijaj Czas | A: Animuj Zodiak | X: Koordynaty"},
    {"num": "069", "id": "mod_unicode", "name": "Unicode & UTF-8 Character Inspector", "cat": "Cyber & Hacking", "desc": "Przeglądarka znaków U+xxxx, ramki pseudograficzne CP437, symbole techniczne i kody UTF-8.", "ctrl": "D-Pad Lewo/Prawo: Znak | Góra/Dół: ±16 Znaków | A: Kod Hex"},
    {"num": "070", "id": "mod_battery_bench", "name": "Battery Benchmark & Hardware Profiler", "cat": "Narzędzia & Net", "desc": "Rejestracja krzywej rozładowania ogniwa 3000 mAh, kondycja baterii i profile poboru prądu.", "ctrl": "D-Pad: Profil Obciążenia | A: Uruchom Test | Y: Eksport CSV"},
    {"num": "071", "id": "mod_binaural", "name": "Binaural Beats Neuro-Synth & Noises", "cat": "Multimedia & Audio", "desc": "Dźwięki do skupienia na słuchawkach: fale Alpha/Theta oraz czysty szum różowy i brązowy.", "ctrl": "D-Pad: Zmiana Fali | A: Start/Stop | Y: Typ Szumu Tła"},
    {"num": "072", "id": "mod_brain", "name": "Cyber-Simon Brain Trainer & Reaction", "cat": "Gry & 3D", "desc": "Gra pamięci sekwencyjnej na przyciskach ABXY oraz pomiar czasu reakcji w milisekundach.", "ctrl": "ABXY: Odtwórz Kolory | START: Nowa Gra | SELECT: Tylko Refleks"},
    {"num": "073", "id": "mod_units", "name": "Engineering Units Converter", "cat": "Nauka & Kosmos", "desc": "Błyskawiczne przeliczanie: ciśnienie (bar/psi/kPa), moment obrotowy (Nm/ft-lb), moc i energia.", "ctrl": "D-Pad: Kategoria / Wartość | A: Edytuj | X: Odwróć Kierunek"},
    {"num": "074", "id": "mod_hasher", "name": "Multi-Hasher & Checksum Generator", "cat": "Cyber & Hacking", "desc": "Równoległe haszowanie w locie: MD5, SHA-1, SHA-256, CRC32 oraz Base64 z pliku lub tekstu.", "ctrl": "D-Pad: Zmień Tekst | A: Haszuj Plik z SD | Y: Kopiuj Hasz"},
    {"num": "075", "id": "mod_pixel", "name": "Pixel Art Studio & Sprite Painter", "cat": "Multimedia & Audio", "desc": "Edytor grafiki pikselowej 16x16 sterowany D-Padem z paletą barw i eksportem do C/PNG.", "ctrl": "D-Pad: Kursor | A: Postaw Piksel | B: Gumka | X: Kolor | Y: Zapisz"},
    {"num": "076", "id": "mod_sniffer", "name": "Wi-Fi Packet Sniffer & DNS Inspector", "cat": "Cyber & Hacking", "desc": "Podgląd pakietów w sieci bezprzewodowej (ARP, DNS, ICMP), przepustowość i monitor domen.", "ctrl": "D-Pad: Przewijaj Listę | A: Filtr IP/Port | B: Wyczyść | Y: Zapisz PCAP"},
    {"num": "077", "id": "mod_tuner", "name": "Instrument Tuner & Pitch Generator", "cat": "Multimedia & Audio", "desc": "Stroik muzyczny z algorytmem autokorelacji i wzorcowym tonem A4 = 440 Hz / 432 Hz.", "ctrl": "D-Pad: Struna/Nuta | A: Dźwięk Wzorcowy | X: Kalibracja 440/432"},
    {"num": "078", "id": "mod_gravity", "name": "N-Body Gravitational Orbit Simulator", "cat": "Nauka & Kosmos", "desc": "Fizyczna symulacja grawitacji układów planetarnych, manewry sondy i orbity Keplera.", "ctrl": "D-Pad: Manewr Sondą | A: Nowe Ciało | X: Czas 1x/2x/5x | B: Reset"},
    {"num": "079", "id": "mod_turing", "name": "Turing Machine Simulator", "cat": "Nauka & Kosmos", "desc": "Wizualny model z przesuwaną taśmą, głowicą i programami (inkrementacja binarna, zajęty bóbr).", "ctrl": "D-Pad: Przesuń Taśmę | A: Krok Maszyny | X: Run | B: Reset"},
    {"num": "080", "id": "mod_ipam", "name": "Subnet CIDR Matrix & IPAM Planner", "cat": "Cyber & Hacking", "desc": "Klockowa mapa podziału sieci IPv4 na podsieci i VLANy z kontrolą nakładania się adresów.", "ctrl": "D-Pad: Wybór Podsieci | A: Podziel na 2 (/+1) | B: Połącz"},
    {"num": "081", "id": "mod_telehack", "name": "80s ARPANET BBS & Wardialer", "cat": "Cyber & Hacking", "desc": "Terminal w klimacie filmu WarGames (1983): wardialing numerów, mainframe WOPR i bot ELIZA.", "ctrl": "D-Pad: Przewijaj | A: Wyślij Komendę | X: Wardialer | Y: ELIZA"},
    {"num": "082", "id": "mod_fluid", "name": "Real-Time Fluid Dynamics (Navier-Stokes)", "cat": "Nauka & Kosmos", "desc": "Mechanika płynów Naviera-Stokesa w 60 FPS: mieszanie prądów D-Padem i wstrzykiwanie barwnika.", "ctrl": "D-Pad: Mieszaj Ciecz | A: Wstrzyknij Pigment | X: Kolor | B: Czyść"},
    {"num": "083", "id": "mod_rhythm", "name": "Cyber Beat Pocket Tap", "cat": "Gry & 3D", "desc": "Dynamiczna gra rytmiczna w neonowej oprawie chiptune: spadające nuty na 4 tory i combo.", "ctrl": "D-Pad Lewo/Góra/Prawo/A: Trafiaj w Nuty | START: Pauza"},
    {"num": "084", "id": "mod_wireframe_race", "name": "Synthwave Vector Highway 3D", "cat": "Gry & 3D", "desc": "Wektorowy wyścig pseudo-3D w stylu OutRun: neonowa trasa, zachód słońca i punkty kontrolne.", "ctrl": "D-Pad Lewo/Prawo: Sterowanie | A: Nitro Przyspieszenie | B: Hamulec"},
    {"num": "085", "id": "mod_laser_optics", "name": "Laser Matrix & Optics Lab", "cat": "Gry & 3D", "desc": "Łamigłówka optyczna: rozmieszczanie zwierciadeł i pryzmatów, by doprowadzić wiązkę lasera.", "ctrl": "D-Pad: Wybór Lustra | A: Obróć o 45° | X: Pryzmat RGB | B: Reset"},
    {"num": "086", "id": "mod_missile_command", "name": "Cyber Defense Missile Interceptor", "cat": "Gry & 3D", "desc": "Obrona miast przed spadającymi rakietami balistycznymi: wybuchy kasetowe i celownik D-Padem.", "ctrl": "D-Pad: Celownik | A: Bateria Środkowa | L1/R1: Bateria Lewa/Prawa"},
]

print(f"[*] Organizing {len(MODULES_LIST)} modules...")

registry_modules = []

for item in MODULES_LIST:
    num = item["num"]
    raw_id = item["id"]
    canon_id = f"{num}_{raw_id}"
    canon_filename = f"{canon_id}.py"
    raw_filename = f"{raw_id}.py"

    # 1. Locate source file
    source_file = None
    if os.path.exists(os.path.join(STORE_DIR, raw_filename)):
        source_file = os.path.join(STORE_DIR, raw_filename)
    elif os.path.exists(os.path.join(APPS_DIR, raw_filename)):
        source_file = os.path.join(APPS_DIR, raw_filename)
    elif os.path.exists(os.path.join(STORE_DIR, canon_filename)):
        source_file = os.path.join(STORE_DIR, canon_filename)

    if not source_file:
        print(f"[-] Source file not found for {raw_id}")
        continue

    # Read source content
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Save canonical file in store/modules/
    dest_store_file = os.path.join(STORE_DIR, canon_filename)
    with open(dest_store_file, "w", encoding="utf-8") as f:
        f.write(content)

    # In store/modules/, create backward-compatible symlink: mod_xyz.py -> XXX_mod_xyz.py
    link_store = os.path.join(STORE_DIR, raw_filename)
    if os.path.lexists(link_store) and not os.path.samefile(link_store, dest_store_file):
        os.remove(link_store)
    if not os.path.exists(link_store):
        os.symlink(canon_filename, link_store)

    # For base modules (001-027), also write into Apps/BrickDeck/modules/
    if int(num) <= 27:
        dest_app_file = os.path.join(APPS_DIR, canon_filename)
        with open(dest_app_file, "w", encoding="utf-8") as f:
            f.write(content)
        link_app = os.path.join(APPS_DIR, raw_filename)
        if os.path.lexists(link_app) and not os.path.samefile(link_app, dest_app_file):
            os.remove(link_app)
        if not os.path.exists(link_app):
            os.symlink(canon_filename, link_app)

    # Calculate file size
    size_kb = max(8, len(content) // 1024)

    # Build Registry Entry
    entry = {
        "num": num,
        "id": canon_id,
        "legacy_id": raw_id,
        "name": f"{num} // {item['name']}",
        "version": "1.0.0",
        "category": item["cat"],
        "author": "kawaczek",
        "description": item["desc"],
        "size_kb": size_kb,
        "download_url": f"https://raw.githubusercontent.com/kawaczek/brik/main/store/modules/{canon_filename}",
        "controls": item["ctrl"],
        "featured": int(num) in (1, 2, 3, 21, 28, 29, 31, 35, 41, 52, 84, 86),
        "screenshot": f"docs/screenshots/{canon_id}.png"
    }
    registry_modules.append(entry)
    print(f"[+] Reorganized: {canon_id}.py ({size_kb} KB)")

# Save updated registry.json
registry_data = {
    "repo_title": "BrickDeck OS Official App Store",
    "repo_version": "2.0",
    "base_url": "https://raw.githubusercontent.com/kawaczek/brik/main",
    "updated_at": "2026-11-24",
    "total_modules": len(registry_modules),
    "categories": [
        "Wszystkie",
        "Gry & 3D",
        "Cyber & Hacking",
        "Narzędzia & Net",
        "Nauka & Kosmos",
        "Multimedia & Audio"
    ],
    "modules": registry_modules
}

with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
    json.dump(registry_data, f, indent=4, ensure_ascii=False)

print(f"[+] Successfully wrote {len(registry_modules)} modules into {REGISTRY_PATH}")
