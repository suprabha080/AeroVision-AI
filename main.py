"""
================================================================================
AeroVision-AI: Next-Gen Touchless Vision & Gesture Workspace
Main Application Entry Point
================================================================================
Author: Suprabha Regmi (https://github.com/suprabha080)
Repository: AeroVision-AI
License: MIT
================================================================================
"""

import os
import sys
import time
import warnings

# Optimize stdout buffering and suppress background TensorFlow/Protobuf logs
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore')

import cv2
import numpy as np

import config as cfg
from src.core.detector import HandDetector
from src.core.gestures import GestureClassifier
from src.core.mouse_engine import MouseEngine
from src.core.canvas_engine import CanvasEngine
from src.core.media_engine import MediaEngine
from src.ui.hud import HudRenderer


def main():
    print("=" * 65)
    print("  🚀 AeroVision-AI: Next-Gen Touchless Gesture Workspace")
    print(f"  Author : Suprabha Regmi (suprabha080)")
    print(f"  Version: {cfg.APP_VERSION}")
    print("=" * 65)

    # 1. Initialize Core Engines
    detector = HandDetector(
        static_image_mode=cfg.STATIC_IMAGE_MODE,
        max_num_hands=cfg.MAX_NUM_HANDS,
        min_detection_confidence=cfg.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=cfg.MIN_TRACKING_CONFIDENCE
    )
    classifier = GestureClassifier(
        history_len=cfg.GESTURE_HISTORY_LEN,
        pinch_threshold=0.35
    )
    mouse_engine = MouseEngine(cfg)
    canvas_engine = CanvasEngine(cfg)
    media_engine = MediaEngine(cfg)
    hud = HudRenderer(cfg)

    # 2. Open Primary Webcam (DirectShow for Windows)
    cap = cv2.VideoCapture(cfg.CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"⚠️ DirectShow capture failed, falling back to default backend...")
        cap = cv2.VideoCapture(cfg.CAMERA_INDEX)

    if not cap.isOpened():
        print("❌ Error: Unable to access system webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.CAMERA_HEIGHT)
    try:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    except Exception:
        pass

    # Webcam warmup
    warmup_ok = False
    for _ in range(15):
        ret, frame = cap.read()
        if ret and frame is not None:
            warmup_ok = True
            break
        time.sleep(0.08)

    if not warmup_ok:
        print("❌ Error: Webcam opened but failed to stream frames.")
        cap.release()
        return

    # Pre-configure GUI Window
    cv2.namedWindow(cfg.WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)
    try:
        cv2.setWindowProperty(cfg.WINDOW_TITLE, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass

    print("\n✅ System initialized successfully!")
    print("Modes Available:")
    print("  [1] DESKTOP MOUSE  : Cursor navigation, smart scroll, clicks, drag, screenshot")
    print("  [2] AIR CANVAS     : Virtual whiteboard with colors, eraser, snapshot export")
    print("  [3] MEDIA PRESENTER: Presentation slides, distance-based volume slider")
    print("\nControls:")
    print("  - Press 'M' or gesture 🤙 (Shaka) to cycle modes")
    print("  - Press '1', '2', '3' to switch directly to a mode")
    print("  - Press 'C' to clear canvas")
    print("  - Press 'Q' to quit\n")

    current_mode_idx = 0
    active_mode = cfg.AVAILABLE_MODES[current_mode_idx]
    mode_switch_cooldown = 0.0

    frame_errors = 0
    MAX_FRAME_ERRORS = 30

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                frame_errors += 1
                if frame_errors >= MAX_FRAME_ERRORS:
                    print("❌ Error: Camera connection lost.")
                    break
                time.sleep(0.04)
                continue

            frame_errors = 0
            # Flip horizontally for natural mirror interaction
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            hud.update_fps()

            # Process Hand Tracking
            results = detector.process_frame(frame)

            raw_gesture = "NO HAND"
            stable_gesture = "NO HAND"
            confidence = 0.0
            tracking_status = "NO HAND"
            index_pos = None
            middle_pos = None
            hand_center_pos = None
            active_landmarks = None

            if results.multi_hand_landmarks:
                tracking_status = "ACTIVE"
                hand_landmarks = results.multi_hand_landmarks[0]
                active_landmarks = hand_landmarks.landmark

                # Draw skeleton
                detector.draw_skeleton(frame, hand_landmarks, w, h)

                # Classify Gesture
                stable_gesture, raw_gesture, confidence = classifier.update(active_landmarks)

                # Key Points
                tip8 = active_landmarks[8]
                index_pos = (int(tip8.x * w), int(tip8.y * h))

                tip12 = active_landmarks[12]
                middle_pos = (int(tip12.x * w), int(tip12.y * h))

                mcp9 = active_landmarks[9]
                hand_center_pos = (int(mcp9.x * w), int(mcp9.y * h))

            else:
                classifier.reset()

            # Mode Switch via Shaka Gesture
            now = time.time()
            if stable_gesture == "MODE SWITCH" and now >= mode_switch_cooldown:
                current_mode_idx = (current_mode_idx + 1) % len(cfg.AVAILABLE_MODES)
                active_mode = cfg.AVAILABLE_MODES[current_mode_idx]
                mode_switch_cooldown = now + 1.2
                print(f"[AeroVision] Switched mode to: {active_mode}")

            # Draw interaction guide boundary
            hud.draw_interaction_box(frame)

            # Route to Active Engine
            status_text = "STANDBY"
            toast_text = "NONE"
            toast_expiry = 0.0

            if active_mode == cfg.MODE_DESKTOP_MOUSE:
                status_text = mouse_engine.step(
                    stable_gesture=stable_gesture,
                    raw_gesture=raw_gesture,
                    index_pos=index_pos,
                    hand_center_pos=hand_center_pos,
                    frame_w=w,
                    frame_h=h
                )
                toast_text = mouse_engine.hud_action
                toast_expiry = mouse_engine.hud_action_expiry

            elif active_mode == cfg.MODE_AIR_CANVAS:
                status_text = canvas_engine.step(
                    stable_gesture=stable_gesture,
                    index_pos=index_pos,
                    middle_pos=middle_pos,
                    frame=frame
                )
                toast_text = canvas_engine.action_msg
                toast_expiry = canvas_engine.action_expiry

            elif active_mode == cfg.MODE_MEDIA_PRESENTER:
                status_text = media_engine.step(
                    stable_gesture=stable_gesture,
                    landmarks=active_landmarks,
                    frame=frame
                )
                toast_text = media_engine.hud_action
                toast_expiry = media_engine.hud_action_expiry

            # Draw Glassmorphism HUD Panels
            hud.draw_telemetry_card(
                frame=frame,
                active_mode=active_mode,
                tracking_status=tracking_status,
                stable_gesture=stable_gesture,
                confidence=confidence,
                status_msg=status_text
            )
            hud.draw_legend_card(frame=frame, active_mode=active_mode)
            hud.draw_action_toast(frame=frame, text=toast_text, expiry_time=toast_expiry)
            hud.draw_footer_bar(frame=frame, active_mode=active_mode)

            # Display Window
            cv2.imshow(cfg.WINDOW_TITLE, frame)

            # Key Controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\n[AeroVision] User requested exit.")
                break
            elif key == ord('m') or key == ord('M'):
                current_mode_idx = (current_mode_idx + 1) % len(cfg.AVAILABLE_MODES)
                active_mode = cfg.AVAILABLE_MODES[current_mode_idx]
                print(f"[AeroVision] Keyboard switched mode to: {active_mode}")
            elif key == ord('1'):
                current_mode_idx = 0
                active_mode = cfg.MODE_DESKTOP_MOUSE
            elif key == ord('2'):
                current_mode_idx = 1
                active_mode = cfg.MODE_AIR_CANVAS
            elif key == ord('3'):
                current_mode_idx = 2
                active_mode = cfg.MODE_MEDIA_PRESENTER
            elif key == ord('c') or key == ord('C'):
                canvas_engine.clear()

    except Exception as e:
        print(f"❌ Unexpected runtime exception: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        print("[AeroVision] Cleaning up hardware and window resources...")
        mouse_engine.release_cleanup()
        detector.close()
        cap.release()
        cv2.destroyAllWindows()
        print("[AeroVision] Shutdown complete.")


if __name__ == "__main__":
    main()
