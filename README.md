# 🚀 AeroVision-AI: Next-Gen Touchless Vision & Gesture Workspace

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8.svg?logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-00C0FF.svg?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-0.9.54-orange.svg)](https://pyautogui.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/suprabha080)

**An intelligent, touchless desktop interface and AR virtual workspace powered by real-time computer vision and machine learning.**

[Features](#-key-features) • [Installation](#-installation--setup) • [Operating Modes](#-operating-modes) • [Gesture Guide](#-gesture-cheat-sheet) • [Architecture](#-project-architecture) • [Author](#-author)

</div>

---

## 🌟 Overview

**AeroVision-AI** transforms any standard webcam into a high-precision, low-latency spatial input device. By tracking 21 3D hand landmarks in real time with Google MediaPipe and OpenCV, AeroVision provides touchless desktop navigation, an augmented reality air canvas, and a presentation/media controller—eliminating physical mouse and keyboard dependency.

Engineered with **adaptive dynamic cursor acceleration**, **recovery stroke absorption**, **hysteresis filtering**, and a **cyberpunk glassmorphism HUD**, AeroVision-AI delivers a frictionless, sci-fi desktop experience.

---

## ✨ Key Features

- 🎯 **Adaptive Precision Cursor Tracking**:
  - Non-linear acceleration curve: slow movements enable fine-grain sub-pixel targeting, while quick gestures sweep across multi-monitor or 4K displays effortlessly.
  - Scale-invariant geometry: normalizes landmark distances against palm dimensions, guaranteeing consistent gesture trigger sensitivity regardless of hand distance from the camera.
  - Exponential moving average (EMA) jitter suppression for stable cursor control without perceptible latency.

- 🖱️ **Full Desktop Mouse Emulation**:
  - **Left Click**: Natural index-and-thumb pinch with visual ripple.
  - **Right Click**: Peace / Victory sign (2 fingers).
  - **Double Click**: Three fingers extended.
  - **Drag & Drop**: Pinch to grab, fold into a fist to drag across the screen, open hand to drop.
  - **Touchless Scrolling**: Fluid vertical scrolling with momentum deadband and return-stroke cancellation.
  - **Browser Navigation**: Four fingers extended for instant `Alt + Left` back navigation.
  - **Instant Screenshot**: Rock-on / Horns gesture automatically captures and saves desktop snapshots.

- 🎨 **Augmented Reality Air Canvas**:
  - Draw smoothly in 3D air using your index finger.
  - Interactive top floating toolbar: **Cyan**, **Pink**, **Green**, **Orange**, **Eraser**, **Clear All**, and **Save to Disk**.
  - Dual-state cursor: Two fingers to hover & select tools; one finger to draw.
  - High-resolution alpha-blended rendering with anti-aliasing.

- 🎬 **Presentation & Media Master**:
  - **Distance-based Volume Slider**: Dynamically adjusts Windows system volume based on the physical distance between your thumb and index fingertips, accompanied by an on-screen HUD gauge (0%–100%).
  - **Slide Navigation**: Move forward or backward through slides during presentations with quick two-finger and three-finger gestures.
  - **Play/Pause Toggle**: Clench into a fist to toggle playback.

- 🖥️ **Sci-Fi Cyberpunk HUD**:
  - Semi-transparent glassmorphism HUD overlays with real-time telemetry (FPS counter, gesture confidence, active mode badge, and status feed).
  - Mode-adaptive gesture legend that dynamically updates depending on whether you're navigating, drawing, or presenting.
  - Boundary guidelines with animated corner brackets.

---

## 🕹️ Operating Modes

Switch modes instantly at any time by pressing **`M`** on your keyboard or flashing the **🤙 Shaka (Hang Loose)** gesture:

| Mode | Shortcut | Primary Purpose | Key Gestures |
| :--- | :---: | :--- | :--- |
| **Desktop Mouse** | `1` or `M` | General OS navigation & productivity | Point, Pinch, Peace, 3-Fingers, Drag, Scroll, Screenshot |
| **Air Canvas** | `2` or `M` | Virtual whiteboard & air sketching | Point (Draw), Peace (Select/Hover), Toolbar Colors |
| **Media & Slides** | `3` or `M` | Presentations, movies & Spotify | Pinch Gap (Volume), Peace (Next), 3-Fingers (Prev), Fist (Pause) |

---

## 🖐️ Gesture Cheat Sheet

```
+-----------------------------------------------------------------------------------+
|  POINT (1 Finger)          PINCH (Thumb + Index)         PEACE (2 Fingers)        |
|       👆                         🤏                            ✌️                 |
|  Move Mouse & Scroll       Single Left Click             Right Click / Next Slide |
+-----------------------------------------------------------------------------------+
|  3 FINGERS                 FOUR FINGERS                  HORNS / ROCK-ON          |
|       🖖                         🖐️ (Thumb Tucked)             🤟                 |
|  Double Click / Prev       Browser Back (Alt+Left)       Save Screenshot (PNG)    |
+-----------------------------------------------------------------------------------+
|  PINCH + FIST              OPEN PALM                     SHAKA / HANG LOOSE       |
|       ✊                         ✋                            🤙                 |
|  Drag & Drop (Hold)        Pause Standby / Mute          Switch Operating Mode    |
+-----------------------------------------------------------------------------------+
```

---

## 🏗️ Project Architecture

```
AeroVision-AI/
├── config.py                 # Central configuration (thresholds, sensitivities, colors)
├── main.py                   # Main event loop, camera pipeline & mode dispatcher
├── requirements.txt          # Python dependencies
├── run.bat                   # 1-Click launcher for Windows
├── run.ps1                   # PowerShell launcher
├── LICENSE                   # MIT License
├── README.md                 # Documentation & Architecture Guide
├── screenshots/              # Captured screenshots & saved air drawings
└── src/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── detector.py       # MediaPipe Hand Landmark extractor & geometry math
    │   ├── gestures.py       # Gesture classifier & majority-vote debouncing
    │   ├── mouse_engine.py   # Adaptive cursor motion, clicking, drag & scroll
    │   ├── canvas_engine.py  # Air Canvas whiteboard, toolbar & stroke rendering
    │   └── media_engine.py   # Touchless volume slider & slide deck controller
    └── ui/
        ├── __init__.py
        ├── hud.py            # Glassmorphism panels, telemetry widgets & toasts
        └── theme.py          # Futuristic neon color palettes & aesthetics
```

---

## ⚡ Installation & Setup

### Prerequisites
- Python **3.10**, **3.11**, or **3.12**
- Built-in or external USB Webcam
- Windows 10/11, macOS, or Linux

### 1. Clone the Repository
```bash
git clone https://github.com/suprabha080/AeroVision-AI.git
cd AeroVision-AI
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch AeroVision-AI
```bash
# Using standard Python
python main.py

# Or on Windows, double-click run.bat
```

---

## ⚙️ Configuration & Customization

All operational parameters are cleanly isolated in [`config.py`](config.py). You can customize:

- **`BASE_SMOOTH_FACTOR`**: Adjust cursor smoothing latency vs instantaneous snap (default: `4.5`).
- **`ACCELERATION_FACTOR`**: Non-linear multiplier for sweeping across large displays (default: `1.35`).
- **`SCROLL_TRIGGER_DISTANCE`**: Vertical sensitivity threshold for scrolling (default: `45px`).
- **`MARGIN_X`, `MARGIN_Y`**: Size of the comfortable camera tracking bounding box.
- **`CANVAS_PALETTE`**: Add or modify colors, tools, and brush thicknesses.

---

## 🛡️ Boundary & Safety Engineering

- **Self-Interaction Protection**: Cursor coordinates are monitored. When the cursor hovers directly over the AeroVision application window, click and scroll commands are suppressed to prevent unintended window traps.
- **Directional Hysteresis**: Touchless scrolling tracks recovery momentum. When relaxing your hand after a scroll pulse, opposite upward movement is absorbed and ignored.
- **Fail-Safe Cleanup**: Emergency cleanup handlers ensure active mouse drags and hardware captures are cleanly released upon application exit (`Q` or `ESC`).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

## 👤 Author

**Suprabha Regmi**
- GitHub: [@suprabha080](https://github.com/suprabha080)
- Email: [regmi2006nepal@gmail.com](mailto:regmi2006nepal@gmail.com)

⭐ If you found this project helpful or inspiring, please consider giving it a **Star** on GitHub!
