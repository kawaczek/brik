"""
BrickDeck UI Theme - Tactical Cyberdeck Color Palette & Dimensions
"""

# Screen Dimensions for TrimUI Brick
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
HEADER_HEIGHT = 52
FOOTER_HEIGHT = 44
VIEWPORT_Y = HEADER_HEIGHT
VIEWPORT_HEIGHT = SCREEN_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT  # 672 px

# Color Palette (RGB tuples for PIL)
COLOR_BG_DARK       = (13, 17, 23)       # Deep night space #0D1117
COLOR_PANEL_BG      = (22, 27, 34)       # Tactical card background #161B22
COLOR_PANEL_ALT     = (28, 33, 40)       # Secondary panel #1C2128
COLOR_BORDER        = (48, 54, 61)       # Subtle border #30363D
COLOR_BORDER_LIGHT  = (75, 85, 99)       # Active border

# Primary & Secondary Accents
COLOR_CYBER_CYAN    = (0, 216, 255)      # Electric Cyan #00D8FF
COLOR_FLIPPER_AMBER = (255, 138, 0)      # Flipper Orange #FF8A00
COLOR_PHOSPHOR_GREEN= (57, 211, 83)      # Hacker Green #39D353
COLOR_NEON_PINK     = (255, 42, 109)     # Cyberpunk Pink #FF2A6D
COLOR_ELECTRIC_BLUE = (30, 144, 255)     # Deep Blue
COLOR_WARNING_YELLOW= (240, 180, 0)      # Warning Yellow

# Text Colors
COLOR_TEXT_PRIMARY   = (240, 246, 252)   # Crisp white #F0F6FC
COLOR_TEXT_SECONDARY = (139, 148, 158)   # Muted gray #8B949E
COLOR_TEXT_MUTED     = (90, 98, 108)     # Dim gray

# Status Colors
COLOR_STATUS_OK      = (57, 211, 83)
COLOR_STATUS_WARN    = (240, 180, 0)
COLOR_STATUS_ERR     = (255, 42, 109)

# Pre-encoded 32-bit BGRA bytes for Framebuffer fast-path
def rgb_to_bgra(rgb_tuple, alpha=255) -> bytes:
    r, g, b = rgb_tuple
    return bytes([b, g, r, alpha])

BGRA_BG_DARK = rgb_to_bgra(COLOR_BG_DARK)
BGRA_PANEL_BG = rgb_to_bgra(COLOR_PANEL_BG)
BGRA_CYAN = rgb_to_bgra(COLOR_CYBER_CYAN)
BGRA_AMBER = rgb_to_bgra(COLOR_FLIPPER_AMBER)
BGRA_GREEN = rgb_to_bgra(COLOR_PHOSPHOR_GREEN)
