import cv2
import mediapipe as mp
import numpy as np

# ── Constants ────────────────────────────────────────────────────────────────
COLORS = [(255, 0, 255), (0, 255, 0), (0, 255, 255), (0, 165, 255)]
COLOR_NAMES = ["Pink", "Green", "Yellow", "Orange"]
BRUSH_THICKNESS = 5
ERASER_RADIUS = 40

# ── MediaPipe Setup ──────────────────────────────────────────────────────────
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ── Webcam ───────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot open webcam. Check camera index or permissions.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Read one frame first to get actual dimensions
ret, init_frame = cap.read()
if not ret:
    print("ERROR: Cannot read frame from webcam.")
    cap.release()
    exit()

h, w = init_frame.shape[:2]

# ── Canvas ───────────────────────────────────────────────────────────────────
canvas = np.zeros((h, w, 3), dtype=np.uint8)

prev_x, prev_y = 0, 0
color_idx = 0
draw_color = COLORS[color_idx]
color_switch_cooldown = 0  # prevents rapid color flickering

# ── Main Loop ────────────────────────────────────────────────────────────────
try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # BUG FIX: resize canvas if frame dims change mid-session
        if canvas.shape[:2] != (h, w):
            canvas = np.zeros((h, w, 3), dtype=np.uint8)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        mode = "PAUSE"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark
                tips = [4, 8, 12, 16, 20]
                fingers = []

                # Thumb — after mirror flip, right-hand thumb open = tip.x < base.x
                fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)

                # Other four fingers — up when tip is above two joints below
                for tip in tips[1:]:
                    fingers.append(1 if landmarks[tip].y < landmarks[tip - 2].y else 0)

                total_fingers = sum(fingers)
                x = int(landmarks[8].x * w)
                y = int(landmarks[8].y * h)

                cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)

                # ── DRAW MODE: only index finger raised ──────────────────────
                if fingers == [0, 1, 0, 0, 0]:
                    mode = "DRAW"
                    if prev_x == 0 and prev_y == 0:
                        prev_x, prev_y = x, y
                    cv2.line(canvas, (prev_x, prev_y), (x, y), draw_color, BRUSH_THICKNESS)
                    prev_x, prev_y = x, y

                # ── COLOR SWITCH: index + middle finger raised (peace sign) ──
                elif fingers == [0, 1, 1, 0, 0]:
                    mode = "COLOR"
                    prev_x, prev_y = 0, 0
                    if color_switch_cooldown == 0:
                        color_idx = (color_idx + 1) % len(COLORS)
                        draw_color = COLORS[color_idx]
                        color_switch_cooldown = 20  # frames to wait before switching again

                # ── ERASER MODE: closed fist ──────────────────────────────────
                elif total_fingers == 0:
                    mode = "ERASER"
                    cv2.circle(canvas, (x, y), ERASER_RADIUS, (0, 0, 0), cv2.FILLED)
                    prev_x, prev_y = 0, 0

                # ── PAUSE MODE: any other gesture ────────────────────────────
                else:
                    mode = "PAUSE"
                    prev_x, prev_y = 0, 0

        # Cooldown tick
        if color_switch_cooldown > 0:
            color_switch_cooldown -= 1

        # Overlay drawing canvas on live frame
        frame = cv2.add(frame, canvas)

        # ── HUD ──────────────────────────────────────────────────────────────
        hud_colors = {
            "DRAW":   (0, 255, 255),
            "ERASER": (0, 80, 255),
            "PAUSE":  (180, 180, 180),
            "COLOR":  (255, 255, 0)
        }
        cv2.putText(frame, f"Mode: {mode}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, hud_colors[mode], 2)

        # Show current color swatch + name
        cv2.rectangle(frame, (10, 55), (40, 85), draw_color, cv2.FILLED)
        cv2.putText(frame, f"Color: {COLOR_NAMES[color_idx]}", (48, 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2)

        # Color palette preview bar (top right)
        for i, col in enumerate(COLORS):
            bx = w - 40 - i * 35
            cv2.rectangle(frame, (bx, 10), (bx + 28, 38), col, cv2.FILLED)
            if i == color_idx:
                cv2.rectangle(frame, (bx - 2, 8), (bx + 30, 40), (255, 255, 255), 2)

        cv2.putText(frame,
                    "Index=Draw | Peace=Color | Fist=Erase | C=Clear | S=Save | ESC=Quit",
                    (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        cv2.imshow("Gesture Vision — Air Drawing", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:                              # ESC → quit
            break
        elif key in (ord('c'), ord('C')):          # C → clear canvas
            canvas = np.zeros((h, w, 3), dtype=np.uint8)
        elif key in (ord('s'), ord('S')):          # S → save drawing
            filename = "air_drawing.png"
            cv2.imwrite(filename, canvas)
            print(f"Drawing saved as {filename}")

finally:
    # Always release webcam even if code crashes
    cap.release()
    cv2.destroyAllWindows()