# 🚍 Dokumentacja API: MZK Gorzów Wielkopolski (System Trapeze SIP)

Dokumentacja inżynierii wstecznej portalu informacji pasażerskiej `https://komunikacja.um.gorzow.pl/vm/main`.

System udostępnia pełne dane telemetryczne GPS floty pojazdów, tablice odjazdów w czasie rzeczywistym, geometrię tras oraz odczyty z miejskich czujników jakości powietrza.

* **Base URL:** `https://komunikacja.um.gorzow.pl/vm/main`
* **Format danych:** Głównie `JSON` (część widoków `HTML`)
* **Wymagane uwierzytelnianie:** **Brak** (otwarty dostęp bez klucza API)
* **SSL / TLS:** Standardowe zapytania HTTPS

---

## 📑 Spis Treści

1. [Telemetria GPS Pojazdów na Żywo](#1-telemetria-gps-pojazdów-na-żywo)
2. [Odjazdy z Przystanków w Czasie Rzeczywistym](#2-odjazdy-z-przystanków-w-czasie-rzeczywistym)
3. [Baza Przystanków i Infrastruktury](#3-baza-przystanków-i-infrastruktury)
4. [Czujniki Jakości Powietrza i Smogu](#4-czujniki-jakości-powietrza-i-smogu)
5. [Narzędzia Pomocnicze i Planer](#5-narzędzia-pomocnicze-i-planer)
6. [Przykłady Wywołań (cURL & Python)](#6-przykłady-wywołań-curl--python)

---

## 1. Telemetria GPS Pojazdów na Żywo

### 1.1 Wszystkie Aktywne Pojazdy w Ruchu
Zwraca aktualną pozycję GPS każdego autobusu i tramwaju poruszającego się w danej sekundzie po Gorzowie.

* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=v`
* **Format:** `application/json`
* **Przykładowa odpowiedź:**
```json
[
  {
    "id": "655",
    "label": "33",
    "lineId": "33",
    "lineLabel": "122",
    "linetype": "3",
    "lat": 52.734986,
    "lon": 15.280774,
    "time": 0,
    "bearing": 0.0,
    "depid": 220362691,
    "type": "Autobus",
    "trip": ""
  },
  {
    "id": "303",
    "label": "41",
    "lineId": "41",
    "lineLabel": "3",
    "linetype": "0",
    "lat": 52.763122,
    "lon": 15.276161,
    "time": 0,
    "bearing": 0.0,
    "depid": 220380413,
    "type": "Tramwaj",
    "trip": ""
  }
]
```
* **Opis pól:**
  * `id`: Numer boczny pojazdu (np. Solaris `#655`, Pesa Twist `#303`).
  * `lineLabel`: Oficjalny numer linii widoczny dla pasażerów (`"122"`, `"3"`).
  * `type`: `"Autobus"` lub `"Tramwaj"`.
  * `lat`, `lon`: Koordynaty GPS z satelity.
  * `bearing`: Kąt zwrotu pojazdu (w stopniach, 0–360°).
  * `depid`: Identyfikator realizowanego kursu rozkładowego.

---

### 1.2 Pojedynczy Pojazd
Śledzenie wybranego wozu po jego numerze bocznym.

* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=v&vid={vehicle_id}`
* **Parametry:** `vid` (np. `655`)
* **Format:** `application/json`

---

### 1.3 Geometria Trasy i Ślad GPS Kursu
Zwraca pełną geometrię drogi/torowiska (polilinię GPS) oraz wszystkie kolejne przystanki dla danego kursu.

* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=vr&did={depid}`
* **Parametry:** `did` (pobrane z pola `depid` z endpointu `action=v`)
* **Format:** `application/json`
* **Kluczowe pola odpowiedzi:**
  * `vehicle`: bieżące dane pojazdu,
  * `line`: informacje o linii,
  * `shape`: tablica setek punktów GPS (`latitude`, `longitude`, `order`), tworzących wektorową trasę przejazdu na mapie,
  * `stops`: chronologiczna lista wszystkich przystanków na trasie z ich koordynatami.

---

### 1.4 Kolejne Przystanki w Trasie (Passing Times)
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=pt&id={depid}&next=5`
* **Format:** `text/html` (panel z przewidywanymi czasami przyjazdu na najbliższe przystanki).

---

### 1.5 Wykaz Linii i Przypisanych Wozów
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=vl` (Wszystkie linie)
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=lvl&lid={line_id}` (Wozy na wybranej linii)

---

## 2. Odjazdy z Przystanków w Czasie Rzeczywistym

### 2.1 Tablica Odjazdów (Format JSON)
Endpoint zasilający wirtualne monitory przystankowe w Gorzowie.

* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=fs&action=departures&stop={stop_id}`
* **Parametry:** `stop` – 12-cyfrowy identyfikator przystanku (np. `000000000095` dla Katedry).
* **Format:** `text/html;charset=UTF-8` (treść jest czystym JSON-em)
* **Przykładowa odpowiedź:**
```json
[
  {
    "time": "6 min",
    "line": "3",
    "destination": "Piaski",
    "stop": "Katedra",
    "depInfo": null,
    "platform": ""
  },
  {
    "time": ">>>",
    "line": "104",
    "destination": "Bora-Komorowskiego",
    "stop": "AWF",
    "depInfo": null,
    "platform": ""
  }
]
```
* **Uwagi:**
  * Gdy pole `time` zawiera `">>>"`, pojazd właśnie wjeżdża na przystanek.
  * Gdy pojazd ma nadajnik GPS, podawany jest czas rzeczywisty (np. `"8 min"`).
  * Dla dalszych kursów bez aktywnego GPS podawana jest godzina rozkładowa (np. `"19:45"`).

---

### 2.2 Pełnoekranowy Monitor Przystankowy (HTML)
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=fs&stop={stop_id}`

### 2.3 Najbliższe Przystanki (Nearest Stops)
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=ns&lon={lon}&lat={lat}`
* **Parametry:** `lon`, `lat` (np. `lon=15.2333&lat=52.7333`)

---

## 3. Baza Przystanków i Infrastruktury

### 3.1 Pełna Baza Przystanków (mstops)
Zawiera wszystkie 418 przystanków w Gorzowie wraz z koordynatami GPS i numerami słupków.

* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=basicdata&action=mstops`
* **Format:** `application/json`
* **Przykładowy rekord:**
```json
{
  "id": "000000000095",
  "alt_id": "8",
  "name": "Katedra",
  "address": "",
  "lat": 52.7313055809705,
  "lon": 15.2380800247192,
  "linetype": "0",
  "platform": ""
}
```

### 3.2 Lekka Baza Przystanków (stops)
Szybka lista przystanków bez koordynatów (26 KB zamiast 61 KB).

* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=basicdata&action=stops`

---

## 4. Czujniki Jakości Powietrza i Smogu

MZK Gorzów posiada sieć **15 czujników jakości powietrza** zainstalowanych na wiatach przystankowych i masztach SIP.

### 4.1 Odczyty na Żywo ze Wszystkich Czujników
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=aqsd`
* **Format:** `application/json`
* **Przykładowa odpowiedź:**
```json
[
  {
    "lat": 52.73309544705093,
    "lon": 15.239793971606392,
    "pm10": 10.067961,
    "pm2_5": 8.368932,
    "info": "Bardzo dobry",
    "code": 0,
    "type": "PM10",
    "station": false,
    "time": "23.11.2026 18:57"
  }
]
```

### 4.2 Progi i Skala Oceny Smogu
* **URL:** `GET https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=aql`

---

## 5. Narzędzia Pomocnicze i Planer

* **Zegar serwera centrali:**  
  `GET https://komunikacja.um.gorzow.pl/vm/main?command=fs&action=clock` -> zwraca tekst `"HH:MM:SS"`.
* **Wyszukiwarka adresów / Geokoder:**  
  `GET https://komunikacja.um.gorzow.pl/vm/main?command=geocoder&names={fraza}`
* **Geokodowanie odwrotne:**  
  `GET https://komunikacja.um.gorzow.pl/vm/main?command=geocoder&action=reverse&lon={lon}&lat={lat}`
* **Planer Podróży (Routing):**  
  `GET https://komunikacja.um.gorzow.pl/vm/main?command=rsearch&a={id_skąd}&b={id_dokąd}&d={data}&t={godzina}&tt=dep&tm=5&v=0`

---

## 6. Przykłady Wywołań (cURL & Python)

### Pobranie aktywnych pojazdów (cURL):
```bash
curl -k "https://komunikacja.um.gorzow.pl/vm/main?command=planner&action=v"
```

### Pobranie odjazdów z Katedry (Python):
```python
import urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://komunikacja.um.gorzow.pl/vm/main?command=fs&action=departures&stop=000000000095"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req, context=ctx) as resp:
    departures = json.loads(resp.read().decode("utf-8"))
    for d in departures:
        print(f"Linia {d['line']} -> {d['destination']}: {d['time']}")
```
