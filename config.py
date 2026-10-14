"""
================================================================================
AeroVision-AI: Next-Gen AI Touchless Vision & Gesture Workspace
Configuration Module
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
Repository: AeroVision-AI
License: MIT
================================================================================
"""

import os
from pathlib import Path

# Application Metadata
APP_NAME = "AeroVision-AI"
APP_VERSION = "2.4.0"
WINDOW_TITLE = "AeroVision AI - Touchless Vision Workspace"

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Camera Capture Settings
CAMERA_INDEX = 0               # 0 is the primary system webcam
CAMERA_WIDTH = 640             # Frame width
CAMERA_HEIGHT = 480            # Frame height
FPS_TARGET = 30                # Target frames per second

# MediaPipe Hand Tracking Settings
STATIC_IMAGE_MODE = False
MAX_NUM_HANDS = 1              # Set to 1 for high performance & minimal latency
MIN_DETECTION_CONFIDENCE = 0.75
MIN_TRACKING_CONFIDENCE = 0.65

# Screen Margins (Webcam Pixels)
# Provides comfortable bounding box so the user does not need to reach the frame edge
MARGIN_X = 85
MARGIN_Y = 65

# Adaptive Cursor Movement Tuning
BASE_SMOOTH_FACTOR = 4.5       # Exponential moving average filter factor
ACCELERATION_FACTOR = 1.35     # Non-linear velocity booster for fast movement
CURSOR_DEADZONE_PX = 2         # Micro-jitter filter for pixel stabilization

# Operating Modes
MODE_DESKTOP_MOUSE = "MOUSE"
MODE_AIR_CANVAS = "CANVAS"
MODE_MEDIA_PRESENTER = "MEDIA"
AVAILABLE_MODES = [MODE_DESKTOP_MOUSE, MODE_AIR_CANVAS, MODE_MEDIA_PRESENTER]

# Debounce & Temporal Stabilization
GESTURE_HISTORY_LEN = 6        # Rolling buffer length for majority-vote classification

# Gesture Confirmation Thresholds (in consecutive frames)
MIN_PINCH_CONFIRM = 2          # ~65ms
MIN_RIGHT_CLICK_CONFIRM = 4    # ~130ms
MIN_DOUBLE_CLICK_CONFIRM = 4   # ~130ms
MIN_FOUR_FINGERS_CONFIRM = 3   # ~100ms
MIN_SCREENSHOT_CONFIRM = 6     # ~200ms
MIN_FIST_CONFIRM = 2           # ~65ms
MIN_FIST_RELEASE = 4           # Consecutive frames to release drag
MIN_NEUTRAL_CONFIRM = 3        # Frames required in neutral to clear action lock

# Gesture Cooldowns (seconds)
PINCH_COOLDOWN = 0.45
RIGHT_CLICK_COOLDOWN = 0.55
DOUBLE_CLICK_COOLDOWN = 0.60
FOUR_FINGERS_COOLDOWN = 0.75
SCREENSHOT_COOLDOWN = 1.80
DRAG_ARM_TIMEOUT = 2.0
ACTION_LOCK_MIN_DURATION = 0.35

# Touchless Vertical Scrolling
SCROLL_TRIGGER_DISTANCE = 45   # Pixels relative to baseline
SCROLL_DEADZONE = 18           # Tremor absorption deadband
SCROLL_COOLDOWN = 0.35         # Minimum seconds between scroll steps
SCROLL_CLICKS = 140            # Scroll sensitivity unit
DIRECTION_REVERSAL_DELAY = 0.60# Suppresses accidental opposite scrolling during recovery

# Media & Presentation Mode Tuning
VOLUME_MAX_DISTANCE = 0.85     # Normalized pinch distance for 100% volume
VOLUME_MIN_DISTANCE = 0.12     # Normalized pinch distance for 0% volume
SLIDE_SWIPE_COOLDOWN = 0.75    # Cooldown for presentation slide transitions

# Air Canvas Settings
CANVAS_BRUSH_THICKNESS = 6
CANVAS_ERASER_THICKNESS = 32
CANVAS_PALETTE = [
    {"name": "CYAN",    "color": (255, 255, 0),    "rect": (20, 10, 100, 50)},
    {"name": "PINK",    "color": (255, 0, 255),    "rect": (115, 10, 195, 50)},
    {"name": "GREEN",   "color": (50, 255, 50),    "rect": (210, 10, 290, 50)},
    {"name": "ORANGE",  "color": (0, 165, 255),    "rect": (305, 10, 385, 50)},
    {"name": "ERASER",  "color": (0, 0, 0),        "rect": (400, 10, 480, 50)},
    {"name": "CLEAR",   "color": (40, 40, 40),     "rect": (495, 10, 575, 50)},
    {"name": "SAVE",    "color": (80, 80, 240),    "rect": (590, 10, 630, 50)},
]

# HUD Theme & Aesthetic Colors (BGR)
COLOR_NEON_BLUE = (255, 200, 0)
COLOR_NEON_CYAN = (255, 240, 0)
COLOR_NEON_PINK = (255, 100, 200)
COLOR_NEON_GREEN = (60, 240, 90)
COLOR_NEON_ORANGE = (40, 150, 255)
COLOR_NEON_PURPLE = (255, 75, 180)
COLOR_DARK_SURFACE = (18, 18, 22)
COLOR_PANEL_BORDER = (75, 80, 95)
COLOR_TEXT_PRIMARY = (245, 245, 250)
COLOR_TEXT_MUTED = (160, 165, 180)
