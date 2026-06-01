import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    gesture = "Unknown"

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = hand_landmarks.landmark

            tips = [4, 8, 12, 16, 20]

            fingers = []

            # Thumb
            if landmarks[tips[0]].x < landmarks[tips[0] - 1].x:
                fingers.append(1)
            else:
                fingers.append(0)

            # Other fingers
            for tip in tips[1:]:
                if landmarks[tip].y < landmarks[tip - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total_fingers = sum(fingers)

            if total_fingers == 0:
                gesture = "Fist"

            elif total_fingers == 5:
                gesture = "Open Palm"

            elif fingers[1] == 1 and fingers[2] == 1 and total_fingers == 2:
                gesture = "Peace"

            elif fingers[0] == 1 and total_fingers == 1:
                gesture = "Thumbs Up"

    cv2.putText(
        frame,
        gesture,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Gesture Vision", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()