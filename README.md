# gesture-vision-air-draw
Real-time air drawing app using hand gestures — built with Python, OpenCV &amp; MediaPipe. Draw, erase, and switch colors using only your webcam.
# Gesture Vision — Air Drawing

Draw in thin air using only your hand and a webcam. No stylus, no touch screen — just computer vision.

Built with **Python**, **OpenCV**, and **MediaPipe**

---

## Features

- **Draw** — raise only your index finger to paint on screen
- **Color Switch** — peace sign (index + middle) to cycle through 4 colors
- **Eraser** — make a fist to erase
- **Pause** — any other gesture pauses the brush
- **Save** — press `S` to save your drawing as a PNG
- **Clear** — press `C` to wipe the canvas
- **Live HUD** — mode indicator, color swatch, and palette preview bar

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| OpenCV | Webcam feed, drawing, display |
| MediaPipe | Real-time hand landmark detection |
| NumPy | Canvas array operations |

---

## Getting Started

**1. Install dependencies**

pip install opencv-python mediapipe numpy

**2. Run**

python air_draw.py

> Make sure your webcam is connected and permissions are granted.

---

## Gesture Reference

| Gesture | Action |
|---------|--------|
| Index finger only | Draw |
| Index + Middle (peace sign) | Switch color |
| Closed fist | Erase |
| Anything else | Pause brush |

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `C` | Clear canvas |
| `S` | Save drawing as `air_drawing.png` |
| `ESC` | Quit |

---

## How It Works

MediaPipe detects 21 hand landmarks per frame. The app checks which fingertips are raised relative to their base joints, classifies the gesture, and maps it to an action in real time — no ML training required on your end.

---

## Author

Made by - Himakshi Agrawal 
Connect on Linkedin - https://www.linkedin.com/in/himakshi-agrawal-27184440b/
