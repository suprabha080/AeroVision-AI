"""
================================================================================
AeroVision-AI: Hand Landmark Detection & Geometry Engine
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    """
    High-precision Hand Landmark Detector wrapping MediaPipe Hands.
    Provides normalized geometric calculations, finger extension checks,
    and scale-invariant distance measurements.
    """

    def __init__(
        self,
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.65
    ):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

    def process_frame(self, frame):
        """
        Process a BGR video frame and return landmarks and annotated features.
        
        Args:
            frame: BGR numpy image from OpenCV.
            
        Returns:
            results: MediaPipe processing output.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Mark image as not writeable to improve performance
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        return results

    @staticmethod
    def calculate_distance(p1, p2):
        """
        Calculate Euclidean distance between two 2D points.
        Accepts MediaPipe landmarks or (x, y) coordinate tuples.
        """
        x1, y1 = (p1.x, p1.y) if hasattr(p1, 'x') else p1
        x2, y2 = (p2.x, p2.y) if hasattr(p2, 'y') else p2
        return float(np.hypot(x1 - x2, y1 - y2))

    @staticmethod
    def get_palm_size(landmarks):
        """
        Computes scale-normalizing reference distance:
        Distance from wrist (0) to middle finger MCP joint (9).
        """
        return HandDetector.calculate_distance(landmarks[0], landmarks[9])

    @staticmethod
    def is_finger_extended(landmarks, tip_id, pip_id, wrist_id=0):
        """
        Checks whether a finger is extended by comparing the tip distance
        to the wrist versus the intermediate joint (PIP) distance to the wrist.
        Reliable across rotations and tilts.
        """
        wrist = landmarks[wrist_id]
        tip = landmarks[tip_id]
        pip = landmarks[pip_id]

        tip_dist = HandDetector.calculate_distance(tip, wrist)
        pip_dist = HandDetector.calculate_distance(pip, wrist)
        return tip_dist > pip_dist

    @staticmethod
    def get_finger_states(landmarks):
        """
        Returns boolean tuple for all 5 fingers:
        (thumb_open, index_open, middle_open, ring_open, pinky_open)
        """
        index_open = HandDetector.is_finger_extended(landmarks, tip_id=8, pip_id=6)
        middle_open = HandDetector.is_finger_extended(landmarks, tip_id=12, pip_id=10)
        ring_open = HandDetector.is_finger_extended(landmarks, tip_id=16, pip_id=14)
        pinky_open = HandDetector.is_finger_extended(landmarks, tip_id=20, pip_id=18)

        # Thumb extension evaluated relative to pinky MCP base (17)
        thumb_tip_to_pinky_base = HandDetector.calculate_distance(landmarks[4], landmarks[17])
        thumb_mcp_to_pinky_base = HandDetector.calculate_distance(landmarks[2], landmarks[17])
        thumb_open = thumb_tip_to_pinky_base > thumb_mcp_to_pinky_base

        return thumb_open, index_open, middle_open, ring_open, pinky_open

    def draw_skeleton(self, frame, hand_landmarks, width, height, glow=True):
        """
        Draws sleek cyber-styled hand landmarks with neon glow connections.
        """
        landmarks = hand_landmarks.landmark

        # Draw connections
        connections = self.mp_hands.HAND_CONNECTIONS
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]

            pt1 = (int(landmarks[start_idx].x * width), int(landmarks[start_idx].y * height))
            pt2 = (int(landmarks[end_idx].x * width), int(landmarks[end_idx].y * height))

            if glow:
                # Outer glow line
                cv2.line(frame, pt1, pt2, (40, 40, 80), 3, cv2.LINE_AA)
            # Core connection line
            cv2.line(frame, pt1, pt2, (0, 220, 255), 1, cv2.LINE_AA)

        # Draw landmark nodes
        for idx, lm in enumerate(landmarks):
            cx, cy = int(lm.x * width), int(lm.y * height)

            # Highlight tips with larger neon circles
            if idx in (4, 8, 12, 16, 20):
                cv2.circle(frame, (cx, cy), 6, (255, 100, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (cx, cy), 8, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.circle(frame, (cx, cy), 3, (0, 255, 200), -1, cv2.LINE_AA)

    def close(self):
        """Release MediaPipe resources cleanly."""
        self.hands.close()
