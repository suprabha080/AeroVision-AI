"""
================================================================================
AeroVision-AI: Glassmorphism HUD Overlay Engine
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

import time
import cv2
import numpy as np
from .theme import COLORS, get_color


class HudRenderer:
    """
    Renders high-definition semi-transparent glassmorphism panels,
    real-time telemetry widgets, dynamic mode indicators, and action toasts.
    """

    def __init__(self, config):
        self.cfg = config
        self.fps_prev_time = time.time()
        self.fps = 0.0
        self.frame_count = 0

    def update_fps(self):
        """Calculates smoothed frames per second."""
        self.frame_count += 1
        now = time.time()
        elapsed = now - self.fps_prev_time
        if elapsed >= 0.5:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_prev_time = now
        return self.fps

    @staticmethod
    def draw_glass_panel(img, pt1, pt2, bg_color=(16, 16, 22), border_color=(60, 65, 80), alpha=0.78):
        """
        Draws semi-transparent rounded rectangular glass card.
        """
        x1, y1 = pt1
        x2, y2 = pt2
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
        cv2.addWeighted(overlay, alpha, img, 1.0 - alpha, 0, img)
        cv2.rectangle(img, (x1, y1), (x2, y2), border_color, 1, cv2.LINE_AA)

    def draw_interaction_box(self, frame):
        """Draws the comfortable active tracking bounding box."""
        h, w, _ = frame.shape
        mx = self.cfg.MARGIN_X
        my = self.cfg.MARGIN_Y
        cv2.rectangle(frame, (mx, my), (w - mx, h - my), (50, 55, 70), 1, cv2.LINE_AA)
        # Corner aesthetic ticks
        tick_len = 12
        for (cx, cy) in [(mx, my), (w - mx, my), (mx, h - my), (w - mx, h - my)]:
            dx = tick_len if cx == mx else -tick_len
            dy = tick_len if cy == my else -tick_len
            cv2.line(frame, (cx, cy), (cx + dx, cy), (0, 230, 255), 2, cv2.LINE_AA)
            cv2.line(frame, (cx, cy), (cx, cy + dy), (0, 230, 255), 2, cv2.LINE_AA)

    def draw_telemetry_card(self, frame, active_mode, tracking_status, stable_gesture, confidence, status_msg):
        """
        Renders the primary top-left telemetry HUD card.
        """
        self.draw_glass_panel(
            frame,
            (12, 12),
            (260, 155),
            bg_color=COLORS["GLASS_BG"],
            border_color=COLORS["GLASS_BORDER"],
            alpha=0.82
        )

        # Header Title
        cv2.putText(frame, "AEROVISION AI", (22, 34), cv2.FONT_HERSHEY_DUPLEX, 0.62, COLORS["BRAND_CYAN"], 2, cv2.LINE_AA)
        cv2.line(frame, (20, 42), (252, 42), (55, 60, 75), 1, cv2.LINE_AA)

        # Mode Badge
        mode_color = COLORS["BRAND_BLUE"] if active_mode == "MOUSE" else (COLORS["BRAND_PURPLE"] if active_mode == "CANVAS" else COLORS["ACTIVE"])
        cv2.putText(frame, f"MODE [{active_mode}]", (150, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.38, mode_color, 1, cv2.LINE_AA)

        # Line 1: Tracking Status & FPS
        track_col = COLORS["ACTIVE"] if tracking_status == "ACTIVE" else COLORS["DANGER"]
        cv2.putText(frame, "Tracking :", (22, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS["TEXT_MUTED"], 1, cv2.LINE_AA)
        cv2.putText(frame, tracking_status, (100, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.44, track_col, 2 if tracking_status == "ACTIVE" else 1, cv2.LINE_AA)
        cv2.putText(frame, f"{int(self.fps)} FPS", (200, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 160, 160), 1, cv2.LINE_AA)

        # Line 2: Detected Gesture
        gest_col = get_color(stable_gesture, COLORS["TEXT_BRIGHT"])
        cv2.putText(frame, "Gesture  :", (22, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS["TEXT_MUTED"], 1, cv2.LINE_AA)
        cv2.putText(frame, stable_gesture, (100, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.44, gest_col, 2, cv2.LINE_AA)

        # Line 3: Gesture Confidence
        conf_pct = int(confidence * 100)
        cv2.putText(frame, "Confidence:", (22, 106), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS["TEXT_MUTED"], 1, cv2.LINE_AA)
        cv2.rectangle(frame, (105, 98), (185, 106), (35, 40, 50), -1, cv2.LINE_AA)
        fill_w = int((conf_pct / 100.0) * 80)
        cv2.rectangle(frame, (105, 98), (105 + fill_w, 106), (0, 240, 255), -1, cv2.LINE_AA)
        cv2.putText(frame, f"{conf_pct}%", (195, 106), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (200, 200, 200), 1, cv2.LINE_AA)

        # Line 4: Action Status
        cv2.putText(frame, "Status   :", (22, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS["TEXT_MUTED"], 1, cv2.LINE_AA)
        cv2.putText(frame, status_msg[:18], (100, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLORS["TEXT_BRIGHT"], 1, cv2.LINE_AA)

    def draw_legend_card(self, frame, active_mode):
        """
        Renders the dynamic top-right gesture reference card
        tailored to the currently selected mode.
        """
        h, w, _ = frame.shape
        px1, py1 = w - 215, 12
        px2, py2 = w - 12, 162

        self.draw_glass_panel(
            frame,
            (px1, py1),
            (px2, py2),
            bg_color=COLORS["GLASS_BG"],
            border_color=COLORS["GLASS_BORDER"],
            alpha=0.82
        )

        cv2.putText(frame, f"LEGEND - {active_mode}", (px1 + 10, py1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.40, COLORS["TEXT_BRIGHT"], 1, cv2.LINE_AA)
        cv2.line(frame, (px1 + 8, py1 + 25), (px2 - 8, py1 + 25), (55, 60, 75), 1, cv2.LINE_AA)

        if active_mode == "MOUSE":
            entries = [
                ("POINT", "Move & Scroll", (0, 230, 255)),
                ("PINCH", "Left Click", (255, 105, 180)),
                ("2 FINGERS", "Right Click", (255, 80, 255)),
                ("3 FINGERS", "Double Click", (255, 230, 0)),
                ("PINCH+FIST", "Drag & Drop", (0, 165, 255)),
                ("HORNS", "Screenshot", (220, 100, 255)),
                ("OPEN PALM", "Pause Standby", (60, 230, 80))
            ]
        elif active_mode == "CANVAS":
            entries = [
                ("1 FINGER", "Draw / Erase", (0, 230, 255)),
                ("2 FINGERS", "Select / Hover", (255, 80, 255)),
                ("TOP BAR", "Color / Tools", (255, 200, 0)),
                ("OPEN PALM", "Pause / Hover", (60, 230, 80)),
                ("HORNS", "Save Snapshot", (220, 100, 255)),
                ("FIST", "Lift Pen", (50, 130, 255))
            ]
        else:  # MEDIA
            entries = [
                ("PINCH GAP", "Volume Slider", (0, 240, 255)),
                ("2 FINGERS", "Next Slide >>", (255, 80, 255)),
                ("3 FINGERS", "<< Prev Slide", (255, 230, 0)),
                ("FIST", "Play / Pause", (50, 130, 255)),
                ("OPEN PALM", "Mute / Standby", (60, 230, 80))
            ]

        y_pos = py1 + 42
        for g_name, g_desc, g_col in entries:
            cv2.putText(frame, g_name, (px1 + 10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.32, g_col, 1, cv2.LINE_AA)
            cv2.putText(frame, g_desc, (px1 + 92, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (190, 190, 200), 1, cv2.LINE_AA)
            y_pos += 16

    def draw_action_toast(self, frame, text, expiry_time):
        """Renders an action notification toast at bottom-center."""
        now = time.time()
        if now <= expiry_time and text and text != "NONE":
            h, w, _ = frame.shape
            card_w = 260
            card_h = 36
            cx1 = (w - card_w) // 2
            cy1 = h - 85
            cx2 = cx1 + card_w
            cy2 = cy1 + card_h

            self.draw_glass_panel(frame, (cx1, cy1), (cx2, cy2), bg_color=(20, 25, 35), border_color=(0, 230, 255), alpha=0.88)
            cv2.putText(frame, text, (cx1 + 16, cy1 + 24), cv2.FONT_HERSHEY_DUPLEX, 0.48, (0, 240, 255), 1, cv2.LINE_AA)

    def draw_footer_bar(self, frame, active_mode):
        """Renders bottom navigation help bar."""
        h, w, _ = frame.shape
        cv2.putText(
            frame,
            "Mode Toggle: [M] or 🤙 Shaka  |  [Q] to Quit  |  AeroVision AI v2.4",
            (14, h - 14),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (160, 165, 180),
            1,
            cv2.LINE_AA
        )
