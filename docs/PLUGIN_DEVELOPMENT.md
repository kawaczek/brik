# 🛠️ Poradnik Tworzenia Własnych Modułów (Wtyczek) dla BrickDeck OS

Krok po kroku: Jak napisać, ostylować i uruchomić własne narzędzie w środowisku **BrickDeck OS** w mniej niż 5 minut!

---

## 🚀 Szablon Wtyczki (Boilerplate)

Wystarczy stworzyć nowy plik o nazwie `mod_twoja_nazwa.py` w folderze `Apps/BrickDeck/modules/`.

Oto kompletny, działający szablon:

```python
"""
BrickDeck Module: Moje Nowe Narzędzie
Opis Twojego modułu i podłączanych sensorów.
"""

from typing import List, Tuple
from core.module_base import BaseModule
from core.theme import (
    COLOR_CYBER_CYAN, COLOR_FLIPPER_AMBER, COLOR_PHOSPHOR_GREEN,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY
)
from core.i18n import t


class MojeNarzedzieModule(BaseModule):
    name = "Moje Nowe Narzędzie"
    short_name = "MojeTool"
    icon = "⚡"
    accent_color = COLOR_CYBER_CYAN

    def __init__(self, app_context=None):
        super().__init__(app_context)
        self.counter = 0
        self.status_text = "Gotowy do pracy"

    def on_load(self):
        """Wywoływane jednorazowo przy starcie systemu."""
        print("[*] Inicjalizacja MojeTool...")

    def on_activate(self):
        """Wywoływane, gdy użytkownik przełączy się na tę zakładkę."""
        super().on_activate()
        print("[*] Aktywowano MojeTool!")

    def get_hotkey_hints(self) -> List[Tuple[str, str]]:
        """Podpowiedzi przycisków wyświetlane na dolnym pasku."""
        return [
            ("L1/R1", t("common.modules", "Moduły")),
            ("A", "Zwiększ Licznik"),
            ("X", "Resetuj"),
            ("B", t("common.back", "Wróć"))
        ]

    def update(self, dt: float):
        """Aktualizacja logiki biznesowej, liczników i animacji (wywoływane w każdej klatce)."""
        pass

    def render(self, canvas):
        """Rysowanie interfejsu graficznego (obszar roboczy: x: 0..1024, y: 52..724)."""
        # 1. Rysuj główną cyberpunkową kartę roboczą
        canvas.draw_card(
            x=32, y=66, w=960, h=634,
            title="MOJE NOWE CYBERDECK NARZĘDZIE",
            subtitle=f"Status: {self.status_text} | Licznik akcji: {self.counter}",
            border_color=self.accent_color
        )

        # 2. Rysuj wskaźnik mocy / postępu
        canvas.draw_gauge(
            x=60, y=140, w=500, h=18,
            value=self.counter % 100, max_val=100,
            label=f"Postęp operacji: {self.counter % 100}%",
            color=COLOR_PHOSPHOR_GREEN
        )

        # 3. Rysuj odznakę (Badge)
        canvas.draw_badge(600, 136, "STAN: NORMALNY", bg_color=(20, 40, 30), text_color=COLOR_PHOSPHOR_GREEN)

        # 4. Rysuj własne teksty
        font = canvas.draw.getfont()
        canvas.draw.text((60, 200), "Wciśnij [A] na gamepadzie, aby zwiększyć licznik.", fill=COLOR_TEXT_PRIMARY, font=font)
        canvas.draw.text((60, 230), "Wciśnij [X], aby wyzerować stan modułu.", fill=COLOR_TEXT_SECONDARY, font=font)

    def handle_input(self, event: str) -> bool:
        """Obsługa kliknięć przycisków na konsoli."""
        if event in ("BTN_A", "a", "A", " "):
            self.counter += 1
            self.status_text = f"Kliknięto A (wartość: {self.counter})"
            return True
        elif event in ("BTN_X", "x", "X"):
            self.counter = 0
            self.status_text = "Zresetowano licznik!"
            return True
        return False
```

---

## 🎨 Przegląd Komponentów Graficznych (`Canvas`)

Silnik `Canvas` dostarcza gotowe komponenty w taktycznym stylu Sci-Fi:

### 1. Karta z obwódką (`draw_card`)
```python
canvas.draw_card(x=32, y=66, w=960, h=634, title="TYTUŁ KARTY", subtitle="Podtytuł", border_color=COLOR_CYBER_CYAN)
```

### 2. Pasek postępu / Gauge (`draw_gauge`)
```python
canvas.draw_gauge(x=60, y=140, w=400, h=16, value=75, max_val=100, label="Bateria: 75%", color=COLOR_CYBER_CYAN)
```

### 3. Pigułka statusu / Badge (`draw_badge`)
```python
canvas.draw_badge(x=500, y=136, text="AKTYWNY", bg_color=(24, 32, 48), text_color=COLOR_STATUS_OK)
```

### 4. Wykres słupkowy (`draw_bar_chart`)
```python
canvas.draw_bar_chart(x=60, y=280, w=600, h=180, labels=["Ch 1", "Ch 6", "Ch 11"], values=[20, 85, 45], max_val=100)
```

### 5. Wizualizator spektrum audio (`draw_spectrum`)
```python
canvas.draw_spectrum(x=60, y=480, w=500, h=120, values=[10, 25, 60, 80, 45, 90, 30])
```

---

## 🕹️ Zdarzenia Wejścia (`event`)

W metodzie `handle_input(self, event: str)` rozpoznawane są następujące kody:

| Zdarzenie Konsoli | Klawisz PC | Znaczenie |
| :--- | :--- | :--- |
| `"BTN_A"` | `Spacja` / `Enter` | Główny przycisk akcji (A) |
| `"BTN_B"` | `Backspace` / `B` | Przycisk powrotu / wyjścia (B) |
| `"BTN_X"` | `X` | Akcja funkcyjna 1 (X) |
| `"BTN_Y"` | `Y` | Akcja funkcyjna 2 (Y) |
| `"DPAD_UP"` | `Strzałka w górę` / `W` | Krzyżak w górę |
| `"DPAD_DOWN"` | `Strzałka w dół` / `S` | Krzyżak w dół |
| `"DPAD_LEFT"` | `Strzałka w lewo` / `A` | Krzyżak w lewo |
| `"DPAD_RIGHT"` | `Strzałka w prawo` / `D` | Krzyżak w prawo |

---

## 🧵 Operacje Sieciowe i Wielowątkowość

Jeśli Twój moduł odpytuje zewnętrzne API lub fizyczny sensor USB (np. SDR czy kamerę), **nigdy nie blokuj głównego wątku w `update()` ani `render()`!**

Zawsze używaj wątku w tle (`daemon=True`):
```python
import threading

def _fetch_data_async(self):
    def worker():
        try:
            # Długie zapytanie sieciowe lub odczyt USB
            data = self._read_sensor()
            self.latest_data = data
        except Exception as e:
            print(f"[!] Błąd sensora: {e}")

    threading.Thread(target=worker, daemon=True).start()
```
Dzięki temu interfejs konsoli TrimUI Brick zachowuje płynne **60 klatek na sekundę** bez żadnych przycięć!
