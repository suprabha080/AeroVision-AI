"""
================================================================================
AeroVision-AI: Air Canvas & Virtual Whiteboard Engine
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

from datetime import datetime
import os
import time
import cv2
import numpy as np


class CanvasEngine:
    """
    Augmented reality air canvas allowing users to sketch, annotate,
    and erase in 3D air space using intuitive finger gestures.
    """

    def __init__(self, config):
        self.cfg = config
        self.canvas = None
        self.prev_x, self.prev_y = None, None

        # Current drawing attributes
        self.current_color = self.cfg.CANVAS_PALETTE[0]["color"]
        self.current_tool_name = self.cfg.CANVAS_PALETTE[0]["name"]
        self.brush_thickness = self.cfg.CANVAS_BRUSH_THICKNESS

        # Feedback
        self.action_msg = "CANVAS READY"
        self.action_expiry = 0.0

    def init_canvas(self, height, width):
        """Initializes blank 3-channel drawing layer."""
        if self.canvas is None or self.canvas.shape[:2] != (height, width):
            self.canvas = np.zeros((height, width, 3), dtype=np.uint8)

    def clear(self):
        """Clears all strokes on the canvas."""
        if self.canvas is not None:
            self.canvas[:] = 0
            self.action_msg = "CANVAS CLEARED"
            self.action_expiry = time.time() + 1.0

    def save_canvas(self):
        """Saves current air drawing to PNG file."""
        if self.canvas is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.cfg.SCREENSHOTS_DIR / f"air_canvas_{timestamp}.png"
            cv2.imwrite(str(filename), self.canvas)
            print(f"[AeroVision] Air drawing saved: {filename}")
            self.action_msg = "DRAWING SAVED"
            self.action_expiry = time.time() + 1.5

    def check_toolbar_click(self, x, y):
        """
        Tests whether the hover position lies within one of the toolbar icons.
        """
        for item in self.cfg.CANVAS_PALETTE:
            rx1, ry1, rx2, ry2 = item["rect"]
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                name = item["name"]
                if name == "CLEAR":
                    self.clear()
                elif name == "SAVE":
                    self.save_canvas()
                elif name == "ERASER":
                    self.current_tool_name = "ERASER"
                    self.current_color = (0, 0, 0)
                    self.brush_thickness = self.cfg.CANVAS_ERASER_THICKNESS
                    self.action_msg = "TOOL: ERASER"
                    self.action_expiry = time.time() + 0.8
                else:
                    self.current_tool_name = name
                    self.current_color = item["color"]
                    self.brush_thickness = self.cfg.CANVAS_BRUSH_THICKNESS
                    self.action_msg = f"COLOR: {name}"
                    self.action_expiry = time.time() + 0.8
                return True
        return False

    def draw_toolbar(self, frame):
        """Renders top floating tool & palette bar onto the frame."""
        for item in self.cfg.CANVAS_PALETTE:
            rx1, ry1, rx2, ry2 = item["rect"]
            name = item["name"]
            col = item["color"]

            is_active = (name == self.current_tool_name)

            # Button background
            bg_col = col if name not in ("CLEAR", "SAVE", "ERASER") else (35, 35, 45)
            cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), bg_col, -1, cv2.LINE_AA)

            # Active glow outline
            border_col = (255, 255, 255) if is_active else (80, 80, 95)
            border_thick = 2 if is_active else 1
            cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), border_col, border_thick, cv2.LINE_AA)

            # Label text
            text_col = (0, 0, 0) if (name in ("CYAN", "GREEN") and is_active) else (240, 240, 240)
            cv2.putText(
                frame,
                name,
                (rx1 + 10, ry1 + 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                text_col,
                1,
                cv2.LINE_AA
            )

    def step(self, stable_gesture, index_pos, middle_pos, frame):
        """
        Handles air drawing and color selection based on hand posture.
        - Two fingers open (Index + Middle): Hover / Palette Selection mode.
        - One finger open (Index only): Active Drawing mode.
        """
        h, w, _ = frame.shape
        self.init_canvas(h, w)

        status = "CANVAS IDLE"

        # 1. Hover / Selection Mode (Index and Middle fingers extended)
        if stable_gesture in ("RIGHT CLICK", "DOUBLE CLICK") and index_pos is not None:
            tx, ty = index_pos
            self.prev_x, self.prev_y = None, None  # Pen lifted

            # Visual hover crosshair
            cv2.drawMarker(frame, (tx, ty), (255, 255, 255), cv2.MARKER_CROSS, 16, 2, cv2.LINE_AA)
            cv2.circle(frame, (tx, ty), 10, self.current_color, 2, cv2.LINE_AA)

            if ty < 60:
                self.check_toolbar_click(tx, ty)
                status = "PALETTE SELECTION"
            else:
                status = "PEN HOVER"

        # 2. Drawing Mode (Single index finger extended)
        elif stable_gesture == "POINT" and index_pos is not None:
            tx, ty = index_pos

            # If inside toolbar region, don't draw
            if ty < 60:
                self.prev_x, self.prev_y = None, None
                status = "TOOLBAR HOVER"
            else:
                if self.prev_x is None or self.prev_y is None:
                    self.prev_x, self.prev_y = tx, ty

                if self.current_tool_name == "ERASER":
                    # Eraser mode: clear mask on canvas
                    cv2.line(
                        self.canvas,
                        (self.prev_x, self.prev_y),
                        (tx, ty),
                        (0, 0, 0),
                        self.brush_thickness,
                        cv2.LINE_AA
                    )
                    cv2.circle(frame, (tx, ty), self.brush_thickness // 2, (100, 100, 100), 2, cv2.LINE_AA)
                    status = "ERASING"
                else:
                    # Drawing mode: draw anti-aliased line
                    cv2.line(
                        self.canvas,
                        (self.prev_x, self.prev_y),
                        (tx, ty),
                        self.current_color,
                        self.brush_thickness,
                        cv2.LINE_AA
                    )
                    cv2.circle(frame, (tx, ty), self.brush_thickness // 2, self.current_color, -1, cv2.LINE_AA)
                    status = "DRAWING"

                self.prev_x, self.prev_y = tx, ty
        else:
            self.prev_x, self.prev_y = None, None

        # Composite canvas strokes on top of camera frame
        gray_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
        inv_mask = cv2.bitwise_not(mask)

        # Black out the drawing areas in the frame, then add canvas strokes
        frame_bg = cv2.bitwise_and(frame, frame, mask=inv_mask)
        frame[:] = cv2.add(frame_bg, self.canvas)

        # Draw toolbar on top
        self.draw_toolbar(frame)

        return status
