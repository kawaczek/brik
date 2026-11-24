#!/usr/bin/env python3
"""
Gorzów Wielkopolski MZK Transit CLI & Telemetry Tool
Queries official MZK Gorzów API for live GPS vehicles, departures, and smog sensors.
"""

import sys
import ssl
import json
import argparse
import urllib.request
from typing import Optional, List, Dict

BASE_URL = "https://komunikacja.um.gorzow.pl/vm/main"

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def api_get(query: str) -> Optional[dict]:
    url = f"{BASE_URL}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MZK-Gorzow-CLI)"})
    try:
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=6.0) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except Exception as e:
        print(f"[!] Błąd zapytania {url}: {e}", file=sys.stderr)
        return None

def cmd_vehicles(filter_line: Optional[str] = None):
    print("=== MZK GORZÓW WLKP. - POJAZDY W RUCHU NA ŻYWO (GPS) ===")
    data = api_get("command=planner&action=v")
    if not data:
        print("Brak danych z serwera.")
        return

    if filter_line:
        data = [v for v in data if v.get("lineLabel") == filter_line]

    trams = [v for v in data if v.get("type") == "Tramwaj"]
    buses = [v for v in data if v.get("type") == "Autobus"]

    print(f"Łącznie w trasie: {len(data)} wozów (Tramwaje: {len(trams)}, Autobusy: {len(buses)})\n")
    print(f"{'TYP':<10} {'LINIA':<8} {'NR BOCZNY':<12} {'SZEROKOŚĆ (LAT)':<18} {'DŁUGOŚĆ (LON)':<18} {'DEPID'}")
    print("-" * 78)

    for v in sorted(data, key=lambda x: (x.get("type", ""), str(x.get("lineLabel", "")))):
        v_type = v.get("type", "Inny")
        line = v.get("lineLabel", "?")
        vid = v.get("id", "?")
        lat = f"{v.get('lat', 0.0):.6f}"
        lon = f"{v.get('lon', 0.0):.6f}"
        depid = v.get("depid", "")
        print(f"{v_type:<10} {line:<8} #{vid:<11} {lat:<18} {lon:<18} {depid}")

def cmd_stops(search_term: Optional[str] = None):
    print("=== BAZA PRZYSTANKÓW MZK GORZÓW WLKP. ===")
    data = api_get("command=basicdata&action=mstops")
    if not data:
        return

    if search_term:
        data = [s for s in data if search_term.lower() in s.get("name", "").lower() or search_term == s.get("alt_id")]

    print(f"Znaleziono przystanków: {len(data)}\n")
    print(f"{'ID SŁUPKA':<14} {'KOD':<8} {'NAZWA PRZYSTANKU':<32} {'GPS (LAT, LON)'}")
    print("-" * 74)

    for s in data[:50]:
        sid = s.get("id", "")
        alt = s.get("alt_id", "")
        name = s.get("name", "")
        coords = f"{s.get('lat', 0):.5f}, {s.get('lon', 0):.5f}"
        print(f"{sid:<14} {alt:<8} {name:<32} {coords}")

    if len(data) > 50:
        print(f"... i jeszcze {len(data) - 50} innych przystanków.")

def cmd_departures(stop_query: str):
    print(f"=== TABLICA ODJAZDÓW NA ŻYWO DLA: '{stop_query}' ===")
    # Resolve stop ID if name passed
    stop_id = stop_query
    stop_name = stop_query
    if not (stop_query.isdigit() and len(stop_query) == 12):
        stops_data = api_get("command=basicdata&action=mstops")
        if stops_data:
            matches = [s for s in stops_data if stop_query.lower() in s.get("name", "").lower() or stop_query == s.get("alt_id")]
            if matches:
                stop_id = matches[0]["id"]
                stop_name = f"{matches[0]['name']} (słupek {matches[0].get('alt_id', '')})"
            else:
                print(f"[!] Nie znaleziono przystanku o nazwie '{stop_query}'.")
                return

    data = api_get(f"command=fs&action=departures&stop={stop_id}")
    if not data:
        print("Brak najbliższych odjazdów lub przystanek nieobsługiwany.")
        return

    print(f"Przystanek: {stop_name} (ID: {stop_id})\n")
    print(f"{'LINIA':<8} {'KIERUNEK / PĘTLA DOCELOWA':<36} {'CZAS DO ODJAZDU'}")
    print("-" * 62)

    for d in data:
        line = d.get("line", "")
        dest = d.get("destination", "")
        tm = d.get("time", "")
        if ">>>" in tm:
            tm = ">>> ZA CHWILĘ (WJEŻDŻA) <<<"
        print(f"{line:<8} {dest:<36} {tm}")

def cmd_smog():
    print("=== CZUJNIKI JAKOŚCI POWIETRZA I SMOGU MZK GORZÓW WLKP. ===")
    data = api_get("command=planner&action=aqsd")
    if not data:
        print("Brak danych z czujników.")
        return

    print(f"Aktywne stacje pomiarowe: {len(data)}\n")
    print(f"{'LOKALIZACJA GPS':<24} {'PM10':<12} {'PM2.5':<12} {'STAN':<18} {'CZAS ODCZYTU'}")
    print("-" * 80)

    for s in data:
        coords = f"{s.get('lat', 0):.4f}, {s.get('lon', 0):.4f}"
        pm10 = f"{s.get('pm10', 0):.1f} µg/m³"
        pm25 = f"{s.get('pm2_5', 0):.1f} µg/m³"
        info = s.get("info", "---")
        tm = s.get("time", "")
        print(f"{coords:<24} {pm10:<12} {pm25:<12} {info:<18} {tm}")

def main():
    parser = argparse.ArgumentParser(description="Gorzów Wielkopolski MZK Transit CLI")
    parser.add_argument("--vehicles", action="store_true", help="Pokaż pozycje wszystkich autobusów i tramwajów GPS")
    parser.add_argument("--line", type=str, default=None, help="Filtruj pojazdy po numerze linii (np. 122 lub 3)")
    parser.add_argument("--departures", type=str, default=None, help="Pokaż odjazdy na żywo z przystanku (np. 'Katedra')")
    parser.add_argument("--stops", type=str, default=None, nargs="?", const="", help="Przeszukaj bazę przystanków w Gorzowie")
    parser.add_argument("--smog", action="store_true", help="Pokaż odczyty z miejskich czujników jakości powietrza")
    args = parser.parse_args()

    if args.vehicles:
        cmd_vehicles(filter_line=args.line)
    elif args.departures:
        cmd_departures(args.departures)
    elif args.stops is not None:
        cmd_stops(search_term=args.stops if args.stops != "" else None)
    elif args.smog:
        cmd_smog()
    else:
        # Default: show vehicles overview & Katedra departures
        cmd_vehicles()
        print()
        cmd_departures("Katedra")
        print()
        cmd_smog()

if __name__ == "__main__":
    main()
