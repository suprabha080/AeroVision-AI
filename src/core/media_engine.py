"""
================================================================================
AeroVision-AI: Touchless Presentation & Media Control Engine
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

import time
import cv2
import numpy as np
import pyautogui
from .detector import HandDetector


class MediaEngine:
    """
    Touchless controller for media players, video conferences,
    and presentation slide decks (PowerPoint, Google Slides, Keynote).
    """

    def __init__(self, config):
        self.cfg = config

        # Media volume state
        self.prev_volume_level = 50
        self.volume_level = 50
        self.volume_last_sent = 0.0

        # Slide navigation state
        self.slide_cooldown_until = 0.0

        # Play/Pause toggle state
        self.play_pause_cooldown_until = 0.0
        self.fist_confirm = 0

        # Action feedback
        self.hud_action = "MEDIA READY"
        self.hud_action_expiry = 0.0

    def adjust_volume(self, normalized_dist, current_time):
        """
        Calculates volume level from pinch gap distance (0% - 100%)
        and sends volume keys to Windows OS.
        """
        # Map pinch distance to 0..100% volume
        vol_pct = np.interp(
            normalized_dist,
            [self.cfg.VOLUME_MIN_DISTANCE, self.cfg.VOLUME_MAX_DISTANCE],
            [0, 100]
        )
        self.volume_level = int(np.clip(vol_pct, 0, 100))

        if current_time - self.volume_last_sent > 0.12:
            diff = self.volume_level - self.prev_volume_level
            if abs(diff) >= 4:
                steps = abs(diff) // 4
                key = 'volumeup' if diff > 0 else 'volumedown'
                for _ in range(steps):
                    try:
                        pyautogui.press(key)
                    except Exception:
                        pass
                self.prev_volume_level = self.volume_level
                self.volume_last_sent = current_time
                self.hud_action = f"VOLUME {self.volume_level}%"
                self.hud_action_expiry = current_time + 0.6

    def next_slide(self, current_time):
        """Advances to the next presentation slide."""
        if current_time >= self.slide_cooldown_until:
            try:
                pyautogui.press('right')
                self.hud_action = "NEXT SLIDE >>"
                self.hud_action_expiry = current_time + 0.8
                self.slide_cooldown_until = current_time + self.cfg.SLIDE_SWIPE_COOLDOWN
            except Exception:
                pass

    def prev_slide(self, current_time):
        """Returns to the previous presentation slide."""
        if current_time >= self.slide_cooldown_until:
            try:
                pyautogui.press('left')
                self.hud_action = "<< PREV SLIDE"
                self.hud_action_expiry = current_time + 0.8
                self.slide_cooldown_until = current_time + self.cfg.SLIDE_SWIPE_COOLDOWN
            except Exception:
                pass

    def toggle_play_pause(self, current_time):
        """Toggles media play/pause state."""
        if current_time >= self.play_pause_cooldown_until:
            try:
                pyautogui.press('playpause')
                self.hud_action = "PLAY / PAUSE"
                self.hud_action_expiry = current_time + 0.8
                self.play_pause_cooldown_until = current_time + 1.0
            except Exception:
                pass

    def draw_volume_hud(self, frame):
        """Draws a futuristic curved volume gauge on the right side."""
        h, w, _ = frame.shape
        bx1, by1 = w - 60, 140
        bx2, by2 = w - 35, h - 140

        # Background track
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), (30, 30, 40), -1, cv2.LINE_AA)
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), (70, 70, 90), 1, cv2.LINE_AA)

        # Active fill bar
        total_h = by2 - by1
        fill_h = int((self.volume_level / 100.0) * total_h)
        fy = by2 - fill_h

        # Gradient color based on volume level
        bar_color = (0, 240, 255) if self.volume_level < 80 else (0, 100, 255)
        cv2.rectangle(frame, (bx1 + 2, fy), (bx2 - 2, by2 - 2), bar_color, -1, cv2.LINE_AA)

        # Volume percentage label
        cv2.putText(
            frame,
            f"{self.volume_level}%",
            (w - 70, by2 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (240, 240, 240),
            1,
            cv2.LINE_AA
        )
        cv2.putText(
            frame,
            "VOL",
            (w - 65, by1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

    def step(self, stable_gesture, landmarks, frame):
        """
        Executes presentation and media control processing.
        """
        current_time = time.time()
        status = "MEDIA READY"

        if landmarks is not None:
            palm_size = HandDetector.get_palm_size(landmarks)
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            dist = HandDetector.calculate_distance(thumb_tip, index_tip)
            norm_dist = dist / palm_size if palm_size > 0 else 0

            # 1. Volume adjustment using thumb-to-index distance
            if stable_gesture in ("POINT", "PINCH", "WAITING..."):
                self.adjust_volume(norm_dist, current_time)
                status = f"VOLUME ADJUST ({self.volume_level}%)"

            # 2. Next Slide: Peace / 2 Fingers
            elif stable_gesture == "RIGHT CLICK":
                self.next_slide(current_time)
                status = "NEXT SLIDE"

            # 3. Prev Slide: 3 Fingers
            elif stable_gesture == "DOUBLE CLICK":
                self.prev_slide(current_time)
                status = "PREV SLIDE"

            # 4. Play/Pause: Fist toggle
            elif stable_gesture == "FIST":
                self.fist_confirm += 1
                if self.fist_confirm >= 3:
                    self.toggle_play_pause(current_time)
                    self.fist_confirm = 0
                status = "PLAY / PAUSE"
            else:
                self.fist_confirm = 0

        self.draw_volume_hud(frame)
        return status
