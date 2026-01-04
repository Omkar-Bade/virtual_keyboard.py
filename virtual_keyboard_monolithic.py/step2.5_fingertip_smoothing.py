import cv2
import mediapipe as mp

# Webcam
cap = cv2.VideoCapture(0)

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Smoothing variables
prev_x, prev_y = 0, 0
alpha = 0.2   # smoothing factor (0 < alpha <= 1)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Index fingertip
            index_tip = hand_landmarks.landmark[8]
            raw_x = int(index_tip.x * w)
            raw_y = int(index_tip.y * h)

            # Initialize first frame
            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = raw_x, raw_y

            # Apply smoothing
            smooth_x = int(prev_x + alpha * (raw_x - prev_x))
            smooth_y = int(prev_y + alpha * (raw_y - prev_y))

            prev_x, prev_y = smooth_x, smooth_y

            # Draw smoothed fingertip
            cv2.circle(frame, (smooth_x, smooth_y), 10, (0, 255, 0), -1)

            # Show coordinates
            cv2.putText(
                frame,
                f"Smoothed: ({smooth_x}, {smooth_y})",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("Step 2.5 - Fingertip Smoothing", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
