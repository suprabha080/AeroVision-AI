"""
================================================================================
AeroVision-AI: Touchless Desktop Mouse Controller
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

from datetime import datetime
import os
import time
import cv2
import numpy as np
import pyautogui

# Set PyAutoGUI pause to 0 for real-time cursor responsiveness
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False


class MouseEngine:
    """
    Handles touchless desktop cursor movements, clicks, drag-and-drop,
    screenshot captures, and touchless vertical scrolling with adaptive smoothing.
    """

    def __init__(self, config):
        self.cfg = config

        # Obtain screen resolution
        try:
            self.screen_w, self.screen_h = pyautogui.size()
        except Exception:
            self.screen_w, self.screen_h = 1920, 1080

        # Smoothing & coordinate tracking
        self.prev_mouse_x = None
        self.prev_mouse_y = None

        # State Machine: "NORMAL", "DRAG_ARMED", "DRAGGING"
        self.app_state = "NORMAL"
        self.pinch_released = True
        self.pinch_cooldown_until = 0.0
        self.pinch_confirm_frames = 0
        self.pinch_release_frames = 0
        self.drag_armed_time = 0.0
        self.fist_confirm_frames = 0
        self.fist_release_frames = 0

        # Action Lock & Priority State Machine
        self.action_lock = None
        self.action_lock_time = 0.0
        self.neutral_confirm_frames = 0

        # Right click state
        self.right_click_released = True
        self.right_click_cooldown_until = 0.0
        self.right_click_confirm_frames = 0

        # Double click state
        self.double_click_released = True
        self.double_click_cooldown_until = 0.0
        self.double_click_confirm_frames = 0

        # Browser back navigation state
        self.four_fingers_released = True
        self.four_fingers_cooldown_until = 0.0
        self.four_fingers_confirm_frames = 0
        self.four_fingers_release_frames = 0

        # Screenshot state
        self.screenshot_confirm_frames = 0
        self.screenshot_cooldown_until = 0.0

        # Scrolling state
        self.scroll_start_y = None
        self.scroll_cooldown_until = 0.0
        self.last_scroll_time = 0.0
        self.last_scroll_dir = None
        self.last_scroll_dir_time = 0.0
        self.scroll_deadzone_frames = 0

        # HUD Action feedback
        self.hud_action = "NONE"
        self.hud_action_expiry = 0.0

    def is_cursor_over_app_window(self, cursor_x=None, cursor_y=None):
        """
        Check if cursor is hovering over the AeroVision application window
        to protect against self-clicking or unintended window interaction.
        """
        if cursor_x is None or cursor_y is None:
            try:
                pos = pyautogui.position()
                cursor_x, cursor_y = pos.x, pos.y
            except Exception:
                return False

        try:
            rect = cv2.getWindowImageRect(self.cfg.WINDOW_TITLE)
            if rect is not None and len(rect) == 4:
                wx, wy, ww, wh = rect
                if (wx - 10 <= cursor_x <= wx + ww + 10) and (wy - 45 <= cursor_y <= wy + wh + 10):
                    return True
        except Exception:
            pass
        return False

    def update_cursor_movement(self, tip_x, tip_y, frame_w, frame_h):
        """
        Maps webcam landmark coordinates to monitor screen coordinates with
        adaptive acceleration and exponential smoothing.
        """
        # Interpolate coordinates within active margin bounding box
        target_x = np.interp(tip_x, [self.cfg.MARGIN_X, frame_w - self.cfg.MARGIN_X], [0, self.screen_w])
        target_y = np.interp(tip_y, [self.cfg.MARGIN_Y, frame_h - self.cfg.MARGIN_Y], [0, self.screen_h])

        # Clamp safely within display boundaries
        target_x = np.clip(target_x, 2, self.screen_w - 3)
        target_y = np.clip(target_y, 2, self.screen_h - 3)

        if self.prev_mouse_x is None or self.prev_mouse_y is None:
            curr_x = target_x
            curr_y = target_y
        else:
            dx = target_x - self.prev_mouse_x
            dy = target_y - self.prev_mouse_y
            dist = np.hypot(dx, dy)

            # Micro-jitter filter
            if dist < self.cfg.CURSOR_DEADZONE_PX:
                curr_x = self.prev_mouse_x
                curr_y = self.prev_mouse_y
            else:
                # Dynamic speed acceleration: faster hand motion sweeps further across display
                smooth = self.cfg.BASE_SMOOTH_FACTOR
                if dist > 35:
                    smooth = max(2.0, self.cfg.BASE_SMOOTH_FACTOR / self.cfg.ACCELERATION_FACTOR)

                curr_x = self.prev_mouse_x + dx / smooth
                curr_y = self.prev_mouse_y + dy / smooth

        self.prev_mouse_x = curr_x
        self.prev_mouse_y = curr_y

        try:
            pyautogui.moveTo(int(curr_x), int(curr_y))
        except Exception:
            pass

        return int(curr_x), int(curr_y)

    def handle_scrolling(self, tip_y, current_time):
        """
        Processes touchless vertical scrolling with directional hysteresis
        and recovery stroke dampening.
        """
        if self.scroll_start_y is None:
            self.scroll_start_y = tip_y

        now = time.monotonic()
        delta_y = tip_y - self.scroll_start_y

        # Recovery stroke absorption: suppress return movement momentum
        if self.last_scroll_dir == "UP" and delta_y > 0:
            if (current_time - self.last_scroll_dir_time < self.cfg.DIRECTION_REVERSAL_DELAY):
                self.scroll_start_y = tip_y
                delta_y = 0
        elif self.last_scroll_dir == "DOWN" and delta_y < 0:
            if (current_time - self.last_scroll_dir_time < self.cfg.DIRECTION_REVERSAL_DELAY):
                self.scroll_start_y = tip_y
                delta_y = 0

        # Deadzone stabilization
        if abs(delta_y) <= self.cfg.SCROLL_DEADZONE:
            self.scroll_deadzone_frames += 1
            if self.scroll_deadzone_frames >= 5:
                self.scroll_start_y = tip_y
                if (current_time - self.last_scroll_dir_time >= self.cfg.DIRECTION_REVERSAL_DELAY):
                    self.last_scroll_dir = None
        else:
            self.scroll_deadzone_frames = 0

        # Scroll trigger
        if now >= self.scroll_cooldown_until:
            if delta_y <= -self.cfg.SCROLL_TRIGGER_DISTANCE:
                # Scroll UP
                try:
                    pyautogui.scroll(self.cfg.SCROLL_CLICKS)
                    self.hud_action = "SCROLL UP"
                    self.hud_action_expiry = current_time + 0.6
                    self.last_scroll_dir = "UP"
                    self.last_scroll_dir_time = current_time
                except Exception:
                    pass
                self.scroll_start_y = tip_y
                self.scroll_cooldown_until = now + self.cfg.SCROLL_COOLDOWN

            elif delta_y >= self.cfg.SCROLL_TRIGGER_DISTANCE:
                # Scroll DOWN
                try:
                    pyautogui.scroll(-self.cfg.SCROLL_CLICKS)
                    self.hud_action = "SCROLL DOWN"
                    self.hud_action_expiry = current_time + 0.6
                    self.last_scroll_dir = "DOWN"
                    self.last_scroll_dir_time = current_time
                except Exception:
                    pass
                self.scroll_start_y = tip_y
                self.scroll_cooldown_until = now + self.cfg.SCROLL_COOLDOWN

    def take_screenshot(self, current_time):
        """
        Takes full desktop screenshot and saves to timestamps in screenshots folder.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.cfg.SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filename))
            print(f"[AeroVision] Screenshot saved to: {filename}")
            self.hud_action = "SCREENSHOT SAVED"
            self.hud_action_expiry = current_time + 1.2
        except Exception as e:
            print(f"[AeroVision] Screenshot failed: {e}")

    def step(self, stable_gesture, raw_gesture, index_pos, hand_center_pos, frame_w, frame_h):
        """
        Executes one frame of touchless mouse interaction logic.
        """
        current_time = time.time()
        status_label = "IDLE"

        # Action Lock release management
        if stable_gesture in ("POINT", "OPEN PALM", "FIST", "NO HAND"):
            self.neutral_confirm_frames += 1
            if self.neutral_confirm_frames >= self.cfg.MIN_NEUTRAL_CONFIRM:
                if self.action_lock and current_time >= self.action_lock_time + self.cfg.ACTION_LOCK_MIN_DURATION:
                    self.action_lock = None
        else:
            self.neutral_confirm_frames = 0

        # Reset scrolling baseline if not pointing
        if stable_gesture != "POINT":
            self.scroll_start_y = None
            self.scroll_cooldown_until = 0.0

        # ======================================================================
        # STATE 1: NORMAL
        # ======================================================================
        if self.app_state == "NORMAL":
            # Re-arm pinch release
            if stable_gesture in ("POINT", "OPEN PALM"):
                self.pinch_release_frames += 1
                if (self.pinch_release_frames >= 3 and
                        current_time >= self.pinch_cooldown_until and
                        self.action_lock is None):
                    self.pinch_released = True
            elif stable_gesture == "PINCH":
                self.pinch_release_frames = 0

            # Re-arm right click release
            if stable_gesture not in ("RIGHT CLICK", "DOUBLE CLICK", "FOUR FINGERS", "OPEN PALM"):
                if current_time >= self.right_click_cooldown_until and self.action_lock is None:
                    self.right_click_released = True

            # Re-arm double click release
            if stable_gesture not in ("DOUBLE CLICK", "FOUR FINGERS", "OPEN PALM"):
                if current_time >= self.double_click_cooldown_until and self.action_lock is None:
                    self.double_click_released = True

            # Re-arm four fingers release
            if stable_gesture in ("POINT", "OPEN PALM", "FIST", "NO HAND"):
                self.four_fingers_release_frames += 1
                if (self.four_fingers_release_frames >= 3 and
                        current_time >= self.four_fingers_cooldown_until and
                        self.action_lock is None):
                    self.four_fingers_released = True
            elif stable_gesture == "FOUR FINGERS":
                self.four_fingers_release_frames = 0

            # 1. POINT: Cursor Movement & Vertical Scrolling
            if stable_gesture == "POINT" and index_pos is not None:
                tip_x, tip_y = index_pos
                mx, my = self.update_cursor_movement(tip_x, tip_y, frame_w, frame_h)
                status_label = "MOVING CURSOR"

                if not self.is_cursor_over_app_window(mx, my):
                    self.handle_scrolling(tip_y, current_time)
                else:
                    status_label = "HOVER (OVER APP)"

            # 2. PINCH: Left Click
            elif stable_gesture == "PINCH":
                self.pinch_confirm_frames += 1
                if (self.action_lock is None and
                        self.pinch_confirm_frames >= self.cfg.MIN_PINCH_CONFIRM and
                        self.pinch_released and
                        current_time >= self.pinch_cooldown_until):
                    if not self.is_cursor_over_app_window():
                        try:
                            pyautogui.click()
                            self.hud_action = "LEFT CLICK"
                            self.hud_action_expiry = current_time + 0.8
                            status_label = "LEFT CLICK"
                        except Exception:
                            pass
                    self.action_lock = "PINCH"
                    self.action_lock_time = current_time
                    self.pinch_released = False
                    self.pinch_release_frames = 0
                    self.pinch_cooldown_until = current_time + self.cfg.PINCH_COOLDOWN

                    # Arm for drag
                    self.app_state = "DRAG_ARMED"
                    self.drag_armed_time = current_time
                    self.fist_confirm_frames = 0
                else:
                    status_label = "PINCH (HELD)"

            # 3. RIGHT CLICK: 2 Fingers
            elif stable_gesture == "RIGHT CLICK":
                self.right_click_confirm_frames += 1
                if (self.action_lock is None and
                        self.right_click_confirm_frames >= self.cfg.MIN_RIGHT_CLICK_CONFIRM and
                        self.right_click_released and
                        current_time >= self.right_click_cooldown_until):
                    if not self.is_cursor_over_app_window():
                        try:
                            pyautogui.rightClick()
                            self.hud_action = "RIGHT CLICK"
                            self.hud_action_expiry = current_time + 0.8
                            status_label = "RIGHT CLICK"
                        except Exception:
                            pass
                    self.action_lock = "RIGHT_CLICK"
                    self.action_lock_time = current_time
                    self.right_click_released = False
                    self.right_click_cooldown_until = current_time + self.cfg.RIGHT_CLICK_COOLDOWN
                else:
                    status_label = "RIGHT CLICK (READY)"

            # 4. DOUBLE CLICK: 3 Fingers
            elif stable_gesture == "DOUBLE CLICK":
                self.double_click_confirm_frames += 1
                if (self.action_lock is None and
                        self.double_click_confirm_frames >= self.cfg.MIN_DOUBLE_CLICK_CONFIRM and
                        self.double_click_released and
                        current_time >= self.double_click_cooldown_until):
                    if not self.is_cursor_over_app_window():
                        try:
                            pyautogui.doubleClick()
                            self.hud_action = "DOUBLE CLICK"
                            self.hud_action_expiry = current_time + 0.8
                            status_label = "DOUBLE CLICK"
                        except Exception:
                            pass
                    self.action_lock = "DOUBLE_CLICK"
                    self.action_lock_time = current_time
                    self.double_click_released = False
                    self.double_click_cooldown_until = current_time + self.cfg.DOUBLE_CLICK_COOLDOWN
                else:
                    status_label = "DOUBLE CLICK (READY)"

            # 5. FOUR FINGERS: Browser Back
            elif stable_gesture == "FOUR FINGERS":
                self.four_fingers_confirm_frames += 1
                if (self.action_lock is None and
                        self.four_fingers_confirm_frames >= self.cfg.MIN_FOUR_FINGERS_CONFIRM and
                        self.four_fingers_released and
                        current_time >= self.four_fingers_cooldown_until):
                    if not self.is_cursor_over_app_window():
                        try:
                            pyautogui.hotkey('alt', 'left')
                            self.hud_action = "BROWSER BACK"
                            self.hud_action_expiry = current_time + 0.8
                            status_label = "BROWSER BACK"
                        except Exception:
                            pass
                    self.action_lock = "FOUR_FINGERS"
                    self.action_lock_time = current_time
                    self.four_fingers_released = False
                    self.four_fingers_cooldown_until = current_time + self.cfg.FOUR_FINGERS_COOLDOWN
                else:
                    status_label = "BROWSER BACK"

            # 6. SCREENSHOT: Rock-on / Horns
            elif stable_gesture == "SCREENSHOT":
                self.screenshot_confirm_frames += 1
                if (self.screenshot_confirm_frames >= self.cfg.MIN_SCREENSHOT_CONFIRM and
                        current_time >= self.screenshot_cooldown_until):
                    self.take_screenshot(current_time)
                    self.screenshot_cooldown_until = current_time + self.cfg.SCREENSHOT_COOLDOWN
                    self.screenshot_confirm_frames = 0
                    status_label = "SCREENSHOT TAKEN"
                else:
                    status_label = "SCREENSHOT ARMED"

            # 7. OPEN PALM: Pause
            elif stable_gesture == "OPEN PALM":
                self.prev_mouse_x, self.prev_mouse_y = None, None
                status_label = "TRACKING PAUSED"

            # 8. FIST: Idle
            elif stable_gesture == "FIST":
                self.prev_mouse_x, self.prev_mouse_y = None, None
                status_label = "STANDBY"

        # ======================================================================
        # STATE 2: DRAG_ARMED
        # ======================================================================
        elif self.app_state == "DRAG_ARMED":
            if current_time - self.drag_armed_time > self.cfg.DRAG_ARM_TIMEOUT:
                self.app_state = "NORMAL"
                self.fist_confirm_frames = 0
                status_label = "NORMAL"
            elif stable_gesture == "FIST":
                self.fist_confirm_frames += 1
                if self.fist_confirm_frames >= self.cfg.MIN_FIST_CONFIRM:
                    try:
                        pyautogui.mouseDown(button='left')
                        self.hud_action = "DRAG START"
                        self.hud_action_expiry = current_time + 0.8
                        self.app_state = "DRAGGING"
                        self.fist_release_frames = 0
                        self.fist_confirm_frames = 0
                        status_label = "DRAGGING"
                    except Exception:
                        self.app_state = "NORMAL"
            elif stable_gesture in ("OPEN PALM", "POINT", "RIGHT CLICK", "DOUBLE CLICK", "FOUR FINGERS"):
                self.app_state = "NORMAL"
                self.action_lock = None
                status_label = "DRAG CANCELLED"

        # ======================================================================
        # STATE 3: DRAGGING
        # ======================================================================
        elif self.app_state == "DRAGGING":
            if hand_center_pos is not None:
                hx, hy = hand_center_pos
                self.update_cursor_movement(hx, hy, frame_w, frame_h)
            status_label = "DRAGGING ACTIVE"

            if stable_gesture == "FIST":
                self.fist_release_frames = 0
            else:
                self.fist_release_frames += 1
                if self.fist_release_frames >= self.cfg.MIN_FIST_RELEASE:
                    try:
                        pyautogui.mouseUp(button='left')
                        self.hud_action = "DRAG END"
                        self.hud_action_expiry = current_time + 0.8
                    except Exception:
                        pass
                    self.app_state = "NORMAL"
                    self.fist_release_frames = 0
                    self.action_lock = None
                    self.pinch_released = (stable_gesture != "PINCH")
                    status_label = "DROPPED"

        return status_label

    def release_cleanup(self):
        """Emergency cleanup to guarantee mouse release on quit."""
        if self.app_state == "DRAGGING":
            try:
                pyautogui.mouseUp(button='left')
            except Exception:
                pass
            self.app_state = "NORMAL"
