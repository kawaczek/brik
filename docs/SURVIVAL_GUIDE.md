# 🏕️ Podręcznik Przetrwania w Blackoucie i Off-Grid (Survival Field Manual)

Kompletny, praktyczny poradnik przetrwania w sytuacji braku zasilania, awarii infrastruktury oraz w terenie. Zoptymalizowany pod kątem wiedzy natychmiastowej, możliwej do wdrożenia przy użyciu przedmiotów codziennego użytku.

> [!TIP]
> **Dla Twórców i Społeczności:** Moduł konsolowy `mod_survival.py` jest w pełni rozszerzalny! Możesz dodawać własne poradniki w formacie Markdown (`.md`) i JSON bezpośrednio do folderu `Apps/BrickDeck/data/survival/custom/`. Szczegóły znajdziesz w dokumencie [SURVIVAL_SYSTEM_ARCHITECTURE.md](file:///home/kawak/brick/docs/SURVIVAL_SYSTEM_ARCHITECTURE.md).

---

## 📑 Spis Treści
1. [Złote Zasady Przetrwania (Reguła Trójek)](#-1-złote-zasady-przetrwania-reguła-trójek)
2. [Woda Pitna: Pozyskiwanie i Uzdatnianie](#-2-woda-pitna-pozyskiwanie-i-uzdatnianie)
3. [Energia i Zasilanie: Wytwarzanie Prądu z Niczego](#-3-energia-i-zasilanie-wytwarzanie-prądu-z-niczego)
4. [Ciepło, Ogień i Przetrwanie Zimą w Mieszkaniu](#-4-ciepło-ogień-i-przetrwanie-zimą-w-mieszkaniu)
5. [Łączność Kryzysowa i Sygnalizacja SOS](#-5-łączność-kryzysowa-i-sygnalizacja-sos)
6. [Medycyna Polowa i Domowe Elektrolity (ORS)](#-6-medycyna-polowa-i-domowe-elektrolity-ors)

---

## ⏳ 1. Złote Zasady Przetrwania (Reguła Trójek)

W sytuacji kryzysowej priorytety są bezwzględne:

* **3 Minuty** bez tlenu (lub przy gwałtownym krwotoku tętniczym).
* **3 Godziny** bez schronienia w skrajnych warunkach termicznych (hipotermia zabija szybciej niż odwodnienie!).
* **3 Dni** bez wody pitnej (spadek wydolności mózgu i nerek już po 24 godzinach).
* **3 Tygodnie** bez pożywienia (organizm trawi zapasy glikogenu i tłuszczu).

> [!IMPORTANT]
> **Zasada STOP:**
> * **S** (Stop) – Zatrzymaj się, usiądź, weź głęboki oddech, opanuj panikę.
> * **T** (Think) – Pomyśl, jakie jest bezpośrednie zagrożenie.
> * **O** (Observe) – Rozejrzyj się, zidentyfikuj zasoby (woda, schronienie, narzędzia).
> * **P** (Plan) – Zaplanuj kolejne 2 godziny i kolejne 24 godziny.

---

## 💧 2. Woda Pitna: Pozyskiwanie i Uzdatnianie

Człowiek potrzebuje minimum **2–3 litrów wody dziennie** do przetrwania. Woda z kałuż, rzek czy deszczówki zawiera zawiesiny, bakterie (np. E. Coli) oraz pasożyty (Giardia).

### Gdzie szukać wody w mieście i terenie?
1. **Zbiornik spłuczki toaletowej** (woda czysta, o ile nie stosowano chemicznych kostek barwiących).
2. **Bojler / Podgrzewacz wody** (posiada zawór spustowy na dole – od 50 do 120 litrów czystej wody w instalacji domowej).
3. **Zjawisko transpiracji roślin:** Zawież przezroczysty worek foliowy na nasłonecznionej gałęzi liściastej i zawiąż szczelnie sznurkiem. Po kilku godzinach na dnie worka skropli się czysta woda zdatna do picia.
4. **Zbiórka deszczówki:** Rozciągnij plandekę lub folię ze spadkiem do naczynia.

### Metoda 1: Warstwowy Filtr Grawitacyjny (DIY z butelki PET)
Gdy woda jest mętna, musisz usunąć zawiesinę mechaniczną przed dezynfekcją:
1. Odetnij dno plastikowej butelki 1.5L lub 2L.
2. W korku zrób 3 małe dziurki lub owiń szyjkę czystą tkaniną/gazą.
3. Układaj warstwy od dołu do góry:
   * **Dno (przy szyjce):** Kawałek bawełny, waty lub mchu (zatrzymuje drobiny).
   * **Warstwa 1 (Kluczowa):** Pokruszony **węgiel drzewny z ogniska** (węgiel aktywny pochłania toksyny chemiczne i zapachy).
   * **Warstwa 2:** Drobny, przepłukany piasek (zatrzymuje mikro-zawiesiny).
   * **Warstwa 3:** Drobny żwir.
   * **Góra:** Grubsze kamyki (rozbijają strumień wlewanej wody).
4. Przepuść wodę 2–3 razy, aż wylatująca ciecz będzie krystalicznie przezroczysta.

### Metoda 2: Dezynfekcja Biologiczna (Niszczenie Bakterii i Wirusów)
Przefiltrowana woda **nie jest jeszcze bezpieczna biologicznie**! Zastosuj jedną z metod:
* **Gotowanie (Najpewniejsze):** Doprowadź wodę do **burzliwego wrzenia przez minimum 1–3 minuty** (na wysokościach powyżej 2000 m n.p.m. gotuj 5 minut).
* **Metoda SODIS (Dezynfekcja Słoneczna UV):** Nalej przejrzystą wodę do przezroczystej butelki PET i połóż ją poziomo na blaszanym dachu lub folii aluminiowej w pełnym słońcu na **minimum 6 godzin**. Promieniowanie UV-A niszczy DNA patogenów.
* **Jodyna / Płyn Lugola:** 3–5 kropli zwykłej jodyny aptecznej na 1 litr wody. Wymieszaj i odczekaj 30 minut przed wypiciem.

---

## ⚡ 3. Energia i Zasilanie: Wytwarzanie Prądu z Niczego

Konsola TrimUI Brick zużywa zaledwie **1.5 – 2.5 W** energii (bateria 3000 mAh 3.7V = ok. 11 Wh). W czasie blackoucie jest Twoim oknem na świat i bazą wiedzy.

### 1. Akumulator Samochodowy 12V (Kopalnia Energii)
Nawet w rozładowanym aucie akumulator 12V 50Ah posiada **ponad 500 Wh energii** – wystarczy na naładowanie konsoli ponad 40 razy!
* **Podłączenie:** Weź zwykłą ładowarkę samochodową do gniazda zapalniczki USB (12V -> 5V).
* Podłącz przewód z bieguna dodatniego akumulatora (+) do środkowego bolca ładowarki, a biegun ujemny (-) do bocznych blaszek sprężynowych ładowarki.
* Otrzymujesz stabilne gniazdo USB 5V 2A do ładowania TrimUI Brick i smartfonów!

### 2. Improwizowane Dynamo z Silnika Krokowego / Silnika DC
Każdy silnik elektryczny prądu stałego (np. z wkrętarki, drukarki, napędu DVD czy wentylatora) działa w drugą stronę jako **prądnica**:
* **Silnik DC (dwuprzewodowy z zabawek/wkrętarki):** Kręcenie osią generuje napięcie stałe. Wystarczy podłączyć go przez diodę prostowniczą (np. 1N4007) do baterii lub przetwornicy Step-Down 5V.
* **Silnik krokowy (ze starej drukarki 3D/skanera):** Kręcenie ręką generuje bardzo wysokie napięcie nawet przy niskich obrotach! Wymaga mostka prostowniczego Graetza (4 diody) i kondensatora filtrującego, aby uzyskać stały prąd ładowania.

### 3. Złote Zasady Oszczędzania Baterii Konsoli TrimUI Brick
* Zmniejsz jasność ekranu do 20–30% (ekran IPS to 70% zużycia prądu).
* Wyłącz Wi-Fi w menu, gdy nie pobierasz danych pogodowych ani satelitarnych.
* Korzystaj z wbudowanego wygaszacza ekranu (moduł `mod_clock.py`) lub usypiaj konsolę przyciskiem zasilania.

---

## 🔥 4. Ciepło, Ogień i Przetrwanie Zimą w Mieszkaniu

W razie zimowego blackoucie brak prądu oznacza wyłączenie pomp ciepła, pieców gazowych i miejskiego ogrzewania. Mieszkanie wychładza się do temperatury zera w 36–48 godzin.

### 1. Mikro-Klimat w Mieszkaniu (Koncepcja "Pokoju w Pokoju")
* Nie próbuj ogrzewać całego mieszkania! Wybierz **najmniejszy, wewnętrzny pokój** (najlepiej bez ścian szczytowych).
* **Rozstaw w pokoju zwykły namiot turystyczny na łóżku/dywanie** i uszczelnij wejście. Temperatura wewnątrz namiotu dzięki ciepłu ciał 2 osób będzie o 6–10°C wyższa niż w reszcie pokoju!
* Okna zasłoń kocami ratunkowymi NRC (stroną srebrną do wnętrza pokoju, by odbijała promieniowanie podczerwone z powrotem).
* Odizoluj się od podłogi: połóż warstwowo kartony, dywany i materac.

### 2. Rozpalanie Ognia bez Zapałek
* **Bateria 9V lub AA + Wełna stalowa (druciak do naczyń):** Dotknięcie biegunów baterii do cienkiej wełny stalowej natychmiast powoduje rozżarzenie włókien do czerwoności. Przyłóż wcześniej przygotowaną suchą hubkę (wacik z wazeliną, kora brzozy).
* **Bateria z telefonu / 18650 + Pasek folii od gumy do żucia:** Wytnij pasek folii papierowo-aluminiowej z przewężeniem na środku (szerokość 2 mm). Dotknij końców paska do biegunów baterii – przewężenie spłonie jasnym płomieniem.

---

## 🆘 5. Łączność Kryzysowa i Sygnalizacja SOS

Gdy maszty telefonii komórkowej stracą zasilanie awaryjne (baterie na BTS-ach padają po 4–8 godzinach), jedynym źródłem łączności staje się pasmo radiowe.

### Złote Częstotliwości Kryzysowe (Bez Pozwolenia):
* **PMR 446 MHz – Kanał 3 (446.03125 MHz) z tonem CTCSS 33 (Subton 210.7 Hz):** Oficjalny polski kanał ratunkowy i obywatelski (tzw. *"Trójka Ratunkowa"*).
* **PMR 446 MHz – Kanał 7:** Ogólnopolski kanał nasłuchowy łączności kryzysowej i prepperskiej.
* **CB Radio – Kanał 9 (27.065 MHz AM):** Międzynarodowy kanał ratunkowy (Ratunek i Pomoc).
* **CB Radio – Kanał 19 (27.185 MHz AM):** Kanał drogowy kierowców (informacje o przejezdności dróg).

### Optyczny i Dźwiękowy Kod SOS:
* Trzy krótkie, trzy długie, trzy krótkie: **`• • •  — — —  • • •`**
* W nocy użyj ekranu konsoli lub latarki: 3 krótkie mrugnięcia (1s), 3 długie (3s), 3 krótkie (1s).
* W dzień użyj lusterka (heliografu) – błysk słońca odbity od lusterka jest widoczny z odległości ponad 15 km dla załóg śmigłowców ratunkowych!

---

## 🩹 6. Medycyna Polowa i Domowe Elektrolity (ORS)

W warunkach kryzysowych odwodnienie wywołane biegunką, stresem lub wysiłkiem fizycznym zabija w 48 godzin. Sama woda nie nawadnia komórek bez sodu i glukozy.

### Przepis na Domowy Roztwór Nawadniający (WHO ORS Formula):
Wymieszaj dokładnie w **1 litrze czystej, przegotowanej wody**:
* **6 płaskich łyżeczek cukru** (glukoza otwiera pompy sodowo-potasowe w jelitach).
* **1/2 płaskiej łyżeczki soli kuchennej** (chlorek sodu).
* *(Opcjonalnie)*: 1/2 szklanki soku z pomarańczy lub odrobina soku z cytryny (potas).
* Pij małymi łykami co 10–15 minut.

### Tamowanie Masywnych Krwotoków:
* Jeśli krew pulsuje lub tryska pod ciśnieniem (krwotok tętniczy na kończynie), bezpośredni ucisk dłonią przez jałowy opatrunek to krok pierwszy.
* Jeśli ucisk nie działa: załóż stazę taktyczną lub improwizowaną opaskę uciskową (szeroki pasek tkaniny min. 5 cm, nigdy cienki sznurek!) **5–7 cm powyżej rany** (nie na stawie!).
* Włóż pod opaskę mocny patyk (krępulec) i obracaj nim, aż krwawienie całkowicie ustanie. Zablokuj patyk i **zapisz markerem na czole/ręce pacjenta dokładną godzinę założenia stazy** (maksymalny czas bez martwicy kończyny to 2 godziny!).
