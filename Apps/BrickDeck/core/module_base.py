"""
BrickDeck Base Module Class
Every tool/plugin in BrickDeck inherits from BaseModule.
"""

from typing import List, Tuple, Optional


class BaseModule:
    """Base class for all BrickDeck modules."""

    name: str = "Base Module"
    short_name: str = "Module"
    icon: str = "⚙️"
    accent_color: Tuple[int, int, int] = (0, 216, 255)

    def __init__(self, app_context=None):
        self.app = app_context
        self.is_active: bool = False

    def on_load(self):
        """Called once when application initializes."""
        pass

    def on_activate(self):
        """Called when user navigates to this module."""
        self.is_active = True

    def on_deactivate(self):
        """Called when user navigates away from this module."""
        self.is_active = False

    def get_hotkey_hints(self) -> List[Tuple[str, str]]:
        """
        Return list of button badges and descriptions for bottom bar.
        Format: [("L1/R1", "Moduly"), ("D-Pad", "Nawigacja"), ("A", "Wybierz")]
        """
        return [
            ("L1/R1", "Moduly"),
            ("D-Pad", "Ruch"),
            ("A", "Wybierz"),
            ("B", "Wroc")
        ]

    def update(self, dt: float):
        """
        Update module internal logic, timers, animations, network polls.
        dt: elapsed time in seconds since last frame.
        """
        pass

    def render(self, canvas):
        """
        Render module visual content to canvas.
        Viewport bounds: x in [0..1024], y in [52..724].
        """
        raise NotImplementedError

    def handle_input(self, event: str) -> bool:
        """
        Handle gamepad/keyboard events.
        event: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'BTN_A', 'BTN_B', 'BTN_X', 'BTN_Y', 'SELECT', 'START'
        Return True if event was handled.
        """
        return False
