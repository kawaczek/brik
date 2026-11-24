# 🏕️ Architektura Bazy Wiedzy i Modułu Survivalowego BrickDeck OS

Dokumentacja techniczna i podręcznik rozbudowy modułu przetrwania (`mod_survival.py`) oraz silnika danych (`core/survival_engine.py`).

---

## 🏗️ 1. Architektura Oparta o Dane (Data-Driven)

Poprzednio poradnik przetrwania był zakodowany na stałe w kodzie Pythona. Obecna architektura została całkowicie rozdzielona na:
1. **Warstwę Danych (`data/survival/`):** Zewnętrzne pliki JSON i Markdown (`.md`), które można edytować i dodawać bez ingerencji w kod źródłowy aplikacji.
2. **Silnik Parsowania i Indeksowania (`core/survival_engine.py`):** Automatycznie skanuje katalogi, parsuje pliki Markdown/JSON, wyciąga metadane, ostrzeżenia i formatowanie, oraz tworzy indeks wyszukiwania.
3. **Interfejs Użytkownika i Przybornik Narzędzi (`modules/mod_survival.py`):** Interaktywna przeglądarka poradników z karuzelą kategorii, pełnoekranowym czytnikiem oraz zestawem kalkulatorów off-grid (WHO ORS, magazyn energii, kompas słoneczny, racjonowanie wody, atlas węzłów, stroboskop SOS).

---

## 📂 2. Struktura Katalogów

```
Apps/BrickDeck/
├── core/
│   └── survival_engine.py      # Silnik skanowania, parsowania MD/JSON i indeksowania
├── modules/
│   └── mod_survival.py         # Interfejs UI, czytnik i kalkulatory interaktywne
└── data/
    └── survival/
        ├── categories.json     # Rejestr kategorii, kolorów, odznak i ikon
        ├── guides/             # Wbudowane, oficjalne poradniki systemowe (.json)
        └── custom/             # KROK DLA UŻYTKOWNIKA: Tu wrzucaj własne pliki .md lub .json!
```

---

## ✍️ 3. Jak Dodać Własny Poradnik w Formacie Markdown (.md)?

To najprostszy i najszybszy sposób – możesz napisać poradnik w dowolnym edytorze tekstu (np. Notatnik, Obsidian, telefon) i zapisać jako plik `.md` w katalogu:
`Apps/BrickDeck/data/survival/custom/twoj_poradnik.md`

### Szablon Pliku Markdown:

```markdown
# 🪓 Mój Nowy Poradnik Przetrwania
> Kategoria: shelter | Priorytet: HIGH | Badge: PIONIERKA | Tags: szałas, drewno, siekiera

Krótki opis wprowadzający do tematu. Możesz pisać normalny tekst akapitowy.

## 🌲 Przygotowanie Materiału
1. Znajdź stabilne, żywe drzewo jako podporę główną szałasu.
2. Oprzyj o nie grubą żerdź kalenicową pod kątem 45 stopni.
3. Po obu stronach ułóż gęsto cieńsze gałęzie sosnowe lub świerkowe.

## ⚠️ Zasady Bezpieczeństwa
> [!WARNING]
> Nigdy nie buduj schronienia pod suchymi, martwymi konarami (tzw. "widow makers")!

> [!TIP]
> Warstwa liści i mchu o grubości 20 cm zapewnia pełną wodoszczelność przy opadach deszczu.
```

### Dostępne Oznaczenia Bloków (Callouts):
* `> [!WARNING]` lub `> [!CAUTION]` – Wyświetla się jako **czerwona ramka ostrzegawcza** z ikoną `⚠️`.
* `> [!IMPORTANT]` lub `> [!ALERT]` – Wyświetla się jako **bursztynowy alert krytyczny** `🚨`.
* `> [!TIP]` lub `> [!NOTE]` – Wyświetla się jako **zielona/morska ramka wskazówki** `💡`.
* `1. `, `2. ` – Numery kroków formatowane na zielono.
* `• `, `- ` – Listy punktowane.

---

## ⚙️ 4. Jak Dodać Poradnik w Formacie JSON?

Jeśli wolisz ustrukturyzowany format JSON, utwórz plik w `data/survival/guides/nazwa.json` lub `data/survival/custom/nazwa.json`:

```json
{
    "id": "twoj_unikalny_id",
    "category": "water",
    "title": "Tytuł Twojego Poradnika",
    "badge": "FILTRACJA",
    "priority": "HIGH",
    "author": "Twój Nick / Zespół",
    "tags": ["woda", "survival", "filtr"],
    "sections": [
        {
            "heading": "NAGŁÓWEK SEKCJI 1",
            "type": "header",
            "lines": [
                "Pierwsza linijka opisu...",
                "Druga linijka opisu..."
            ]
        },
        {
            "heading": "KROKI WYKONAWCZE",
            "type": "step",
            "lines": [
                "1. Krok pierwszy...",
                "2. Krok drugi..."
            ]
        },
        {
            "heading": "OSTRZEŻENIE",
            "type": "warn",
            "lines": [
                "Krytyczna uwaga dotycząca bezpieczeństwa!"
            ]
        }
    ]
}
```

---

## 🏷️ 5. Dostępne Kategorie (`categories.json`)

Kategorie można modyfikować i dodawać nowe w pliku `Apps/BrickDeck/data/survival/categories.json`:

| ID Kategorii | Ikona | Nazwa Wyświetlana | Przeznaczenie |
| :--- | :---: | :--- | :--- |
| `water` | 💧 | **Woda & Filtracja** | Pozyskiwanie wody, filtry węglowe, SODIS, zbiórka deszczówki |
| `power` | ⚡ | **Energia & Zasilanie** | Akumulatory 12V, dynama, ładowanie USB, baterie |
| `shelter` | 🏕️ | **Schronienie & Zima** | Pokój w pokoju, namioty, folia NRC, izolacja od podłoża |
| `fire` | 🔥 | **Ogień & Ciepło** | Metody bez zapałek, wełna stalowa, sreberko, hubka |
| `nav` | 🧭 | **Nawigacja & Orientacja** | Kompas słoneczny z zegarkiem, Gwiazda Polarna, cień patyka |
| `radio` | 🆘 | **Łączność & SOS** | PMR Kanał 3/33, CB radio, alfabet Morse'a, meldunek METHANE |
| `firstaid` | 🩹 | **Pierwsza Pomoc & Medycyna** | Formuła WHO ORS, staza taktyczna, hipotermia |
| `knots` | 🪢 | **Węzły & Pionierka** | Ratowniczy (Bowline), wyblinka, prusik, szotowy, płaski |
| `food` | 🍃 | **Żywność & Dzika Kuchnia** | Test jadalności roślin, korzenie, pułapki |
| `tools` | 🧮 | **Kalkulatory & Narzędzia** | Interaktywne narzędzia liczące w czasie rzeczywistym |

---

## 🔄 6. Hot-Reloading: Skanowanie Plików w Locie

Nie musisz restartować systemu BrickDeck ani konsoli po dodaniu nowego pliku!
Wystarczy nacisnąć przycisk **`[Y]`** na konsoli w module survivalowym:
* Silnik natychmiast ponownie przeszukuje foldery `guides/` i `custom/`.
* Na ekranie pojawia się zielona plakietka: `Baza odświeżona! (X poradników)`.
* Nowe artykuły pojawiają się natychmiast w swoich kategoriach!

---

## 🧮 7. Rozbudowa Narzędzi Interaktywnych w `mod_survival.py`

W sekcji `tools` (`🧮 Kalkulatory & Narzędzia`) zaimplementowano 5 modułów kalkulacyjnych:
1. **🧪 Kalkulator WHO ORS:** Oblicza proporcje glukozy i soli dla podanej objętości wody oraz masy ciała poszkodowanego.
2. **🔋 Kalkulator Czasu Pracy Baterii:** Dynamicznie przelicza godziny pracy urządzenia (konsola, smartfon, radio) z wybranego akumulatora (12V 50Ah, AGM, 18650, Powerbank).
3. **🧭 Symulator Kompasu Słonecznego:** Rysuje tarczę zegara wskazówkowego, słońce i dwusieczną kąta wyznaczającą oś Północ-Południe.
4. **💧 Planer Zapasów Wody:** Oblicza całkowite zapotrzebowanie (w litrach i kilogramach) na podstawie liczby osób, dni i klimatu.
5. **🪢 Atlas Węzłów Ratowniczych:** Wizualizacja ASCII i instrukcja 5 kluczowych węzłów.
6. **🆘 Awaryjny Flasher SOS (Przycisk `[X]`):** 3 tryby błysków (Morse SOS, Beacon 1Hz, Biała Latarka 100%).

Aby dodać kolejne narzędzie (np. kalkulator pożywienia/kalorii lub szacowanie odległości po huku pioruna), wystarczy dodać wpis do listy `self.tools_list` w `mod_survival.py` oraz metodę `_render_tool_twoja_nazwa()`.
