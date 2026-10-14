"""
================================================================================
AeroVision-AI: Gesture Classification & State Machine
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
================================================================================
"""

from collections import Counter, deque
import time
from .detector import HandDetector


class GestureClassifier:
    """
    Classifies normalized hand landmarks into distinct interactive gestures
    with temporal debouncing, hysteresis filtering, and state management.
    """

    # Gesture Constants
    GESTURE_NONE = "NO HAND"
    GESTURE_WAITING = "WAITING..."
    GESTURE_POINT = "POINT"
    GESTURE_PINCH = "PINCH"
    GESTURE_RIGHT_CLICK = "RIGHT CLICK"
    GESTURE_DOUBLE_CLICK = "DOUBLE CLICK"
    GESTURE_FOUR_FINGERS = "FOUR FINGERS"
    GESTURE_OPEN_PALM = "OPEN PALM"
    GESTURE_FIST = "FIST"
    GESTURE_SCREENSHOT = "SCREENSHOT"
    GESTURE_MODE_SWITCH = "MODE SWITCH"

    def __init__(self, history_len=6, pinch_threshold=0.35):
        self.history_len = history_len
        self.pinch_threshold = pinch_threshold
        self.history = deque(maxlen=history_len)

    def classify_raw(self, landmarks):
        """
        Evaluates 21 normalized landmarks and returns the immediate raw gesture.
        """
        if landmarks is None or len(landmarks) < 21:
            return self.GESTURE_NONE

        palm_size = HandDetector.get_palm_size(landmarks)
        if palm_size == 0:
            return self.GESTURE_WAITING

        thumb_open, index_open, middle_open, ring_open, pinky_open = HandDetector.get_finger_states(landmarks)
        open_count = sum([index_open, middle_open, ring_open, pinky_open])

        # Distance between thumb tip (4) and index tip (8)
        pinch_dist = HandDetector.calculate_distance(landmarks[4], landmarks[8])
        normalized_pinch = pinch_dist / palm_size

        # 1. FIST: All 4 main fingers curled
        if open_count == 0:
            return self.GESTURE_FIST

        # 2. OPEN PALM: All 5 fingers extended
        if open_count == 4 and thumb_open:
            return self.GESTURE_OPEN_PALM

        # 3. FOUR FINGERS: 4 fingers extended, thumb folded/curled
        if open_count == 4 and not thumb_open:
            return self.GESTURE_FOUR_FINGERS

        # 4. MODE SWITCH (Shaka / Hang Loose): Thumb and Pinky open, middle 3 curled
        if thumb_open and pinky_open and not index_open and not middle_open and not ring_open:
            return self.GESTURE_MODE_SWITCH

        # 5. SCREENSHOT (Rock-on / Horns): Index and Pinky open, middle & ring curled
        if index_open and pinky_open and not middle_open and not ring_open:
            return self.GESTURE_SCREENSHOT

        # 6. DOUBLE CLICK (3 Fingers: Index + Middle + Ring open, Pinky curled)
        if index_open and middle_open and ring_open and not pinky_open:
            return self.GESTURE_DOUBLE_CLICK

        # 7. RIGHT CLICK (2 Fingers / Peace Sign: Index + Middle open, Ring & Pinky curled)
        if index_open and middle_open and not ring_open and not pinky_open:
            return self.GESTURE_RIGHT_CLICK

        # 8. PINCH: Thumb and Index tips touching / in close proximity, others curled
        if (normalized_pinch < self.pinch_threshold and
                not middle_open and not ring_open and not pinky_open):
            return self.GESTURE_PINCH

        # 9. POINT: Only Index finger open
        if index_open and not middle_open and not ring_open and not pinky_open:
            return self.GESTURE_POINT

        return self.GESTURE_WAITING

    def update(self, landmarks):
        """
        Updates the history buffer and returns (stable_gesture, raw_gesture, confidence).
        """
        if landmarks is None:
            self.history.clear()
            return self.GESTURE_NONE, self.GESTURE_NONE, 0.0

        raw_gesture = self.classify_raw(landmarks)
        self.history.append(raw_gesture)

        if not self.history:
            return self.GESTURE_NONE, raw_gesture, 0.0

        counts = Counter(self.history)
        most_common, frequency = counts.most_common(1)[0]
        confidence = frequency / len(self.history)

        return most_common, raw_gesture, confidence

    def reset(self):
        """Reset historical buffer."""
        self.history.clear()
