"""
================================================================================
AeroVision-AI: UI Theme & Palette System
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

# Cyberpunk & Futuristic BGR Colors for OpenCV
COLORS = {
    # Brand
    "BRAND_CYAN": (255, 230, 0),
    "BRAND_BLUE": (255, 170, 0),
    "BRAND_PURPLE": (255, 80, 200),
    
    # State Accents
    "ACTIVE": (60, 240, 90),
    "PAUSED": (0, 220, 255),
    "WARNING": (0, 160, 255),
    "DANGER": (60, 70, 240),
    "NEUTRAL": (150, 150, 160),
    
    # Gestures
    "POINT": (0, 230, 255),
    "PINCH": (255, 105, 180),
    "RIGHT CLICK": (255, 80, 255),
    "DOUBLE CLICK": (255, 225, 0),
    "FOUR FINGERS": (255, 165, 0),
    "OPEN PALM": (60, 230, 80),
    "FIST": (50, 130, 255),
    "SCREENSHOT": (220, 100, 255),
    "MODE SWITCH": (0, 255, 180),
    "WAITING...": (150, 150, 150),
    "NO HAND": (100, 100, 100),
    
    # Surfaces
    "GLASS_BG": (16, 16, 22),
    "GLASS_BORDER": (60, 65, 80),
    "TEXT_BRIGHT": (245, 245, 250),
    "TEXT_MUTED": (165, 170, 185)
}


def get_color(key, fallback=(200, 200, 200)):
    """Retrieve color tuple safely with fallback."""
    return COLORS.get(key, fallback)
